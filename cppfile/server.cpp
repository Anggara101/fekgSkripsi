#include <stdio.h>
#include <unistd.h>
#include <sys/socket.h>
#include <thread>
#include <string.h>
#include <errno.h>
#include <algorithm>
#include <numeric>
#include <vector>
#include <sys/time.h>

#include <wiringPi.h>
#include <wiringSerial.h>
#include <bluetooth/bluetooth.h>
#include <bluetooth/rfcomm.h>

bool done_training = false;
bool done_initFilter = false;

char buf[1024] = {0};
char data[1024] = {0};
char bl_buf[1024] = {0};
int s, client, bytes_read, value, fd, endl_i;
int n = 0;
std::vector<double> vEcg;

unsigned long start;
unsigned long t;

long long current_time_ms(){
   struct timeval te; 
   gettimeofday(&te, NULL); // get current time
   long long milliseconds = te.tv_sec*1000LL + te.tv_usec/1000; // calculate milliseconds
   return milliseconds;
}

double sensor(){  
  int i = 0;
  int i_cr = 0;
  while(true){
    value = serialGetchar(fd);
    data[i] = value;
    i++;
    if (value == 13){
      i_cr = i;
    }
    if (value == 10){
      break;
    }      
  }
  n++;
  if(n > 15){
    char c_ecg[20] = {0};
    for(int i_ecg=0; i_ecg<i_cr-1; i_ecg++){
      strncat(c_ecg, &data[i_ecg], 1);
    }
    t = current_time_ms() - start;
    double ecg = atof(c_ecg);
    memset(data, 0, sizeof(data));
    return ecg;
  }
  return 0;
}


void write_bt(double d, int mode){
    char tmp[20]={0x0};
    sprintf(tmp,"%d,%f\n", mode, d);

    write(client, tmp, strlen(tmp));
}

int fs = 2000;
const int len_buf = 0.09 * fs;

/* Global variable for filter parameter */

// Bandpass filter parameter
double b_b[] = {0.00076851, 0.0, -0.00153702, 0.0, 0.00076851};
double a_b[] = {1.0, -3.91536717, 5.75406653, -3.76183614, 0.92314231};
int len_b_b = sizeof(b_b)/sizeof(b_b[0]);
// Derivative filter parameter
double b_d[] = {1.0, 2.0, 0.0, -2.0, -1.0};
int const len_b_d = sizeof(b_d)/sizeof(b_d[0]);
double a_d[len_b_d] = {0};
// Moving average filter parameter
int const window_width = 60;
double b_m[window_width];
int const len_b_m = sizeof(b_m)/sizeof(b_m[0]);
double a_m[len_b_m] = {0};

void initfilter(){
    // Initialize derivative filter parameter
    for(int m=0; m < len_b_d; m++){
        b_d[m] = b_d[m]*fs/8;
    }
    // Initialize MWI filter parameter
    for(int m=0; m < len_b_m; m++){
        b_m[m] = 1.0/window_width;
    }
    done_initFilter = true;
}

double filt(double x[], double y[], int len_b, double b[], double a[]){
    double result = b[0] * x[0];
    for(int m=1; m < len_b; m++){
        result += b[m] * x[m] - a[m] * y[m];
    }
    return result;
}

double v_average(std::vector<double> const& v){
    if(v.empty()){
        return 0;
    }
    return std::accumulate( v.begin(), v.end(), 0.0)/v.size();
}

/* Global variable for clustering */
const int n_cluster = 3;
double centroid[n_cluster];

void kmeans(std::vector<double> X, int len_X, int max_iter = 300, double tol = 0.0001){
    bool diff = true;
    std::vector<double> k1, k2, k3;
    int iter=0;
    int label[len_X] = {0};
    // initialize centroid
    double upper_bound = *std::max_element(X.begin(), X.end());
    centroid[0] = 0.0;
    centroid[1] = 0.08 * upper_bound;
    centroid[2] = 0.8 * upper_bound;
    // Kmeans loop
    while(diff && iter < max_iter){
        // Asign data to nearest centroid
        for(int j=0; j<len_X; j++){
            if(abs(X[j] - centroid[0]) < abs(X[j] - centroid[1]) && 
            abs(X[j] - centroid[0]) < abs(X[j] - centroid[2])){
                label[j] = 0;
                k1.push_back(X[j]);
            }else if (abs(X[j] - centroid[1]) < abs(X[j] - centroid[0]) && 
            abs(X[j] - centroid[1]) < abs(X[j] - centroid[2])){
                label[j] = 1;
                k2.push_back(X[j]);
            }else{
                label[j] = 2;
                k3.push_back(X[j]);
            }
        }
        // Calculate new centroid
        double avr1 = v_average(k1);
        double avr2 = v_average(k2);
        double avr3 = v_average(k3);
        double new_centroid[] = {avr1, avr2, avr3};

        // Look for convergence
        if(abs(new_centroid[0]-centroid[0]) <= tol && abs(new_centroid[1]-centroid[1]) <= tol 
        && abs(new_centroid[2]-centroid[2]) <= tol){
            diff = false;
        }
        printf("iter: %d, %f, %f, %f\n", iter, centroid[0], centroid[1], centroid[2]);
        
        // reset and prepare next iteration
        k1.clear();
        k2.clear();
        k3.clear();
        centroid[0] = new_centroid[0];
        centroid[1] = new_centroid[1];
        centroid[2] = new_centroid[2];
        iter++;
    }
}

void training (){
    
    if((fd=serialOpen("/dev/ttyUSB0",115200)) < 0){
        fprintf(stderr,"Unable to open serial device: %s\n",strerror(errno));
        return;
    }
    FILE * pFile;
    pFile = fopen ("datasensor.csv","w");
    
    start = current_time_ms();
    t = current_time_ms() - start;
  
    // Initialize filter parameter
    if(!done_initFilter){
        initfilter();
    }
  
    // Buffer container
    double ecg_buf[len_buf] = {0};
    double ecg_f_buf[len_buf] = {0};
    double ecg_d_buf[len_buf] = {0};
    double ecg_s_buf[len_buf] = {0};
    double ecg_m_buf0[len_buf] = {0};
    double ecg_m_buf[len_buf] = {0};

    double ecg_raw;
    std::vector<double> vEcg;

    // find peaks parameter
    //double is_peak[10000] = {0};
    double peaks;
    int peaks_i;

    // Peak container
    std::vector<double> peak_vec;
    std::vector<int> peak_i_vec;

    while(t<=10000 && buf[0]== '2'){
        ecg_raw = sensor();
        if(n>15){
            // Asign signal to buffer
            ecg_buf[0] = ecg_raw;
            vEcg.push_back(ecg_raw);
            // Filtering
            ecg_f_buf[0] = filt(ecg_buf, ecg_f_buf, len_b_b, b_b, a_b);
            ecg_d_buf[0] = filt(ecg_f_buf, ecg_d_buf, len_b_d, b_d, a_d)/1000;
            // Squaring
            ecg_s_buf[0] = ecg_d_buf[0]*ecg_d_buf[0];
            // Filtering
            ecg_m_buf0[0] = filt(ecg_s_buf, ecg_m_buf0, len_b_m, b_m, a_m);
            ecg_m_buf[0] = filt(ecg_m_buf0, ecg_m_buf, len_b_m, b_m, a_m);
            write_bt(ecg_raw, 1);
            //printf("%lu,%f,%f\n", t, ecg_raw, ecg_m_buf[0]);
            fprintf (pFile, "%f,%f,%f\n", ecg_buf[0], ecg_f_buf[0], ecg_m_buf[0]);

            // Peak detection
            if(ecg_m_buf[1] > ecg_m_buf[2] && ecg_m_buf[1] >= ecg_m_buf[0]){
                peaks = ecg_m_buf[1];
                peaks_i = t;
                //is_peak[i-1] = peaks;
                // Asign peaks to peak container
                peak_vec.push_back(peaks);
                peak_i_vec.push_back(peaks_i);
                printf("Peaks: %d, %f\n", peaks_i, peaks);
            }

            // reset buffer to prepare for next iteration
            for(int m = len_buf-2; m >= 0; m--){
                ecg_buf[m+1] = ecg_buf[m];
                ecg_f_buf[m+1] = ecg_f_buf[m];
                ecg_d_buf[m+1] = ecg_d_buf[m];
                ecg_s_buf[m+1] = ecg_s_buf[m];
                ecg_m_buf0[m+1] = ecg_m_buf0[m];
                ecg_m_buf[m+1] = ecg_m_buf[m];
            }
        }
    }
    fclose (pFile);
    printf("%d\n", vEcg.size());
    kmeans(peak_vec, peak_vec.size());
    done_training = true;
    return;
}

int mainSensor(){
    if((fd=serialOpen("/dev/ttyUSB0",115200)) < 0){
        fprintf(stderr,"Unable to open serial device: %s\n",strerror(errno));
        return 1;
    }

    double ecg_raw;
    std::vector<double> vEcg;
    start = current_time_ms();
    t = current_time_ms() - start;

    // buffer
    double ecg_buf[len_buf] = {0};
    double ecg_f_buf[len_buf] = {0};
    double ecg_d_buf[len_buf] = {0};
    double ecg_s_buf[len_buf] = {0};
    double ecg_m_buf0[len_buf] = {0};
    double ecg_m_buf[len_buf] = {0};

    // find peaks parameter
    //double is_peak[10000] = {0};
    double peaks;
    int peaks_i;

    // Peak container
    std::vector<double> peak_vec;
    std::vector<int> peak_i_vec;

    // HR container
    double mHR = 0, fHR = 0, fRRavr = 0;
    double mRR[9] = {0}, fRR[9] = {0};
    std::vector<double> mQrs;
    std::vector<double> fQrs;
    std::vector<double> noisePeak;

    n=0;

    while(t<=10000){
        ecg_raw = sensor();
        if(n>15){
            // Asign signal to buffer
            ecg_buf[0] = ecg_raw;
            vEcg.push_back(ecg_raw);
            // Filtering
            ecg_f_buf[0] = filt(ecg_buf, ecg_f_buf, len_b_b, b_b, a_b);
            ecg_d_buf[0] = filt(ecg_f_buf, ecg_d_buf, len_b_d, b_d, a_d)/1000;
            // Squaring
            ecg_s_buf[0] = ecg_d_buf[0]*ecg_d_buf[0];
            // Filtering
            ecg_m_buf0[0] = filt(ecg_s_buf, ecg_m_buf0, len_b_m, b_m, a_m);
            ecg_m_buf[0] = filt(ecg_m_buf0, ecg_m_buf, len_b_m, b_m, a_m);

            //printf("%lu,%f,%f\n", t, ecg_raw, ecg_m_buf[0]);

            // Peak detection
            if(ecg_m_buf[1] > ecg_m_buf[2] && ecg_m_buf[1] >= ecg_m_buf[0]){
                peaks = ecg_m_buf[1];
                peaks_i = t;
                //is_peak[i-1] = peaks;
                // Asign peaks to peak container
                peak_vec.push_back(peaks);
                peak_i_vec.push_back(peaks_i);
                //printf("Peaks: %d, %f\n", peaks_i, peaks);

                // detect mQRS
                if(abs(peaks - centroid[0]) < abs(peaks - centroid[1]) && 
                abs(peaks - centroid[0]) < abs(peaks - centroid[2])){
                  noisePeak.push_back(peaks_i);
                  // std::cout << "noise peak:" << peaks_i << '\n';
                }else if (abs(peaks - centroid[1]) < abs(peaks - centroid[0]) && 
                abs(peaks - centroid[1]) < abs(peaks - centroid[2])){
                  fQrs.push_back(peaks_i);

                  if(fQrs.size() >= 2){
                      fRR[0] = fQrs.end()[-1]-fQrs.end()[-2];
                      
                      // Search Back
                      if(fRR[0] >= 1.66*fRRavr && fRRavr != 0 && mQrs.size()>0){
                          fQrs.push_back(peaks_i);
                          fQrs.end()[-2] = mQrs.end()[-1];
                          fRR[0] = fQrs.end()[-1]-fQrs.end()[-2];
                      }
                      
                      fHR = 60/fRR[0] * 1000000/fs ;
                      int fCount=0;
                      fRRavr = 0;
                      for (int m = 8; m >= 0; m--){
                          fRR[m+1] = fRR[m];
                          if(fRR[m+1] != 0){
                              fCount++;
                              fRRavr += fRR[m+1];
                          }
                      }
                      if(fCount != 0){
                          fRRavr = fRRavr/fCount;
                      }
                  }
                  write_bt(fHR, 2);
                  printf("fHR: %d, %f, %f\n", peaks_i, fHR, fRR[0]);
                  
                }else{
                  mQrs.push_back(peaks_i);

                  if(mQrs.size() >= 2){
                      mRR[0] = mQrs.end()[-1]-mQrs.end()[-2];
                      if(mRR[0] != 0){
                            mHR = 60/mRR[0] * 1000000/fs ;
                      }else{
                          mHR = 0;
                      }
                      /*
                      int mCount=0;
                      mRRavr = 0;
                      for (int m = 8; m >= 0; m--){
                          mRR[m+1] = mRR[m];
                          if(mRR[m+1] != 0){
                              mCount++;
                              mRRavr += mRR[m+1];
                          }
                      }
                      if(mCount != 0){
                          mRRavr = mRRavr/mCount;
                      }
                      */
                  }
                  printf("mHR: %d, %f, %f\n", peaks_i, mHR, mRR[0]);
                  write_bt(mHR, 3);
                }
              
            }

            // reset buffer to prepare for next iteration
            for(int m = len_buf-2; m >= 0; m--){
                ecg_buf[m+1] = ecg_buf[m];
                ecg_f_buf[m+1] = ecg_f_buf[m];
                ecg_d_buf[m+1] = ecg_d_buf[m];
                ecg_s_buf[m+1] = ecg_s_buf[m];
                ecg_m_buf0[m+1] = ecg_m_buf0[m];
                ecg_m_buf[m+1] = ecg_m_buf[m];
            }
        }
    }
    done_training = false;
    return 0;    
}


int serialSensor(){
    int fd ;
    int n = 0;
    int t = 0;
    int start = current_time_ms();

    if((fd=serialOpen("/dev/ttyUSB0",115200)) < 0){
        fprintf(stderr,"Unable to open serial device: %s\n",strerror(errno));
        return 1;
    }
    FILE * pFile;
    pFile = fopen ("datasensor.csv","w");

    for (;;){
        int i = 0;
        int i_cr = 0;
        while(true){
            value = serialGetchar(fd);
            char valuechar = char(value);
            data[i] = valuechar;
            i++;
            if (value == 13){
                i_cr = i;
            }
            if (value == 10){
                break;
            }      
        }
        n++;
        if(n > 15){
            char c_ecg[20] = {0};
            for(int i_ecg=0; i_ecg<i_cr-1; i_ecg++){
                strncat(c_ecg, &data[i_ecg], 1);
            }
            t = current_time_ms() - start;
            double ecg = atof(c_ecg);
            vEcg.push_back(ecg);
            int j=0;
            for(j=0; j<i; j++){
              printf("%c", data[j]);
              fprintf (pFile, "%c", data[j]);
            }
            
            write(client, data, i);
            
            memset(data, 0, sizeof(data));
            if(buf[0] != '2'|| t>10000){
                printf("Sending data completed\n");
                fclose(pFile);
                return 0;
            }
        }
    }
}

int main(int argc, char **argv){
    struct sockaddr_rc loc_addr = { 0 }, rem_addr = { 0 };
    socklen_t opt = sizeof(rem_addr);
    bdaddr_t bdaddr_any =  {{0, 0, 0, 0, 0, 0}};
    // allocate socket
    s = socket(AF_BLUETOOTH, SOCK_STREAM, BTPROTO_RFCOMM);

    // bind socket to port 1 of the first available 
    // local bluetooth adapter
    loc_addr.rc_family = AF_BLUETOOTH;
    loc_addr.rc_bdaddr = bdaddr_any;
    loc_addr.rc_channel = (uint8_t) 1;
    bind(s, (struct sockaddr *)&loc_addr, sizeof(loc_addr));

    // put socket into listening mode
    listen(s, 1);
    while (true){
        fprintf(stderr, "Waiting for connection on RFCOMM channel %i\n", loc_addr.rc_channel);
        // accept one connection
        client = accept(s, (struct sockaddr *)&rem_addr, &opt);

        ba2str( &rem_addr.rc_bdaddr, buf );
        fprintf(stderr, "accepted connection from %s\n", buf);
        done_training = false;
        memset(buf, 0, sizeof(buf));
        while (true){
            // read data from the client
            bytes_read = read(client, buf, sizeof(buf));
            if( bytes_read > 0 ) {
                printf("%s", buf);
                if (buf[0] == '2' && !done_training){
                    std::thread t1(training);
                    printf("training data\n");
                    t1.detach();
                }
                else if (buf[0] == '2' && done_training){
                    std::thread t2(mainSensor);
                    printf("sending data\n");
                    t2.detach();
                }
                
            }
            else if (bytes_read == 0){
                printf("No More Data\n");
                break;
            }
            else{
                printf("Client Disconnected\n");
                break;
            }
        }
    }
    
    // close connection
    close(client);
    close(s);
    return 0;
}
