#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <algorithm>
#include <stdlib.h>
#include <vector>
#include <numeric>

struct point{
    double x, y;
};

/* Global variable */

struct point ekg[60000];
int fs = 1000;
const int len_buf = 0.09 * fs;

/* Global variable for filter parameter */

// Bandpass filter parameter
double b_b[] = {0.00295827, 0.0, -0.00591654, 0.0, 0.00295827};
double a_b[] = {1.0, -3.82193348, 5.49756255, -3.52773632, 0.85219225};
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

/* Global variable for clustering */
const int n_cluster = 3;
double centroid[n_cluster];

void readcsv(std::string filename){
    std::ifstream myFileStream(filename);
    if(!myFileStream.is_open()){
        std::cout<<"File failed to open!!"<<std::endl;
    }
    
    std::string tempstring, line;

    int i = 0;
    while(std::getline(myFileStream, line)){
        std::stringstream ss(line);
        getline(ss, tempstring, ',');
        ekg[i].x = stod(tempstring);
        getline(ss, tempstring, ',');
        ekg[i].y = stod(tempstring);
        // std::cout<< ekg[i].x << ";" << ekg[i].y <<std::endl;
        i++;
    }
    myFileStream.close();
}

double filt(double x[], double y[], int len_b, double b[], double a[]){
    double result = b[0] * x[0];
    for(int m=1; m < len_b; m++){
        result += b[m] * x[m] - a[m] * y[m];
        // std::cout<<y[0]<<std::endl;
    }
    return result;
}

double v_average(std::vector<double> const& v){
    if(v.empty()){
        return 0;
    }

    auto const count = static_cast<double>(v.size());
    return std::reduce(v.begin(), v.end()) / count;
}

int kmeans(std::vector<double> X, int len_X, int max_iter = 300, double tol = 0.0001){
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
        std::cout<<"iter: "<< iter << ", " << centroid[0]<< ", " 
            << centroid[1] << ", " << centroid[2] <<'\n';
        
        // reset and prepare next iteration
        k1.clear();
        k2.clear();
        k3.clear();
        centroid[0] = new_centroid[0];
        centroid[1] = new_centroid[1];
        centroid[2] = new_centroid[2];
        iter++;
    }
    // Datalogging
    std::ofstream outfile2("data/data10/out/data10_abd1_out2_10s.csv");
    for(int m = 0; m < len_X; m++){
        outfile2 << m << ", " << label[m] << '\n';
    }
    outfile2.close();
    // for(int m = 0; m < len_X; m++){
    //     std::cout<< m << "," << label[m] << '\n';
    // }
    return 0;
}

void initfilter(){
    // Initialize derivative filter parameter
    for(int m=0; m < len_b_d; m++){
        b_d[m] = b_d[m]*fs/8;
    }
    // Initialize MWI filter parameter
    for(int m=0; m < len_b_m; m++){
        b_m[m] = 1.0/window_width;
    }
}


int training(std::string fileName){
    // Read data
    readcsv(fileName);

    // Initialize filter parameter
    initfilter();
    
    // Buffer container
    double ecg_buf[len_buf] = {0};
    double ecg_f_buf[len_buf] = {0};
    double ecg_d_buf[len_buf] = {0};
    double ecg_s_buf[len_buf] = {0};
    double ecg_m_buf0[len_buf] = {0};
    double ecg_m_buf[len_buf] = {0};

    // container
    double ecg_m[10000];

    // find peaks parameter
    double is_peak[10000] = {0};
    double peaks;
    int peaks_i;

    // Peak container
    std::vector<double> peak_vec;
    std::vector<int> peak_i_vec;

    // Datalogging
    std::ofstream outfile("data/data10/out/data10_abd1_out_10s.csv");

    //training
    for(int i=0; i<10000; i++){
        // Asign signal to buffer
        ecg_buf[0] = ekg[i].y;
        // Filtering
        ecg_f_buf[0] = filt(ecg_buf, ecg_f_buf, len_b_b, b_b, a_b);
        ecg_d_buf[0] = filt(ecg_f_buf, ecg_d_buf, len_b_d, b_d, a_d)/1000;
        // Squaring
        ecg_s_buf[0] = ecg_d_buf[0]*ecg_d_buf[0];
        // Filtering
        ecg_m_buf0[0] = filt(ecg_s_buf, ecg_m_buf0, len_b_m, b_m, a_m);
        ecg_m_buf[0] = filt(ecg_m_buf0, ecg_m_buf, len_b_m, b_m, a_m);
        // Asign output to container
        ecg_m[i] = ecg_m_buf[0];
        
        // Peak datection
        if(ecg_m_buf[1] > ecg_m_buf[2] && ecg_m_buf[1] >= ecg_m_buf[0]){
            peaks = ecg_m_buf[1];
            peaks_i = i - 1;
            is_peak[i-1] = peaks;
            // Asign peaks to peak container
            peak_vec.push_back(peaks);
            peak_i_vec.push_back(peaks_i);
        }
        
        // outfile << ekg[i].x << "," << ecg_buf[0] << "," << ecg_f_buf[0] << "," << ecg_d_buf[0] << "," <<
        //     ecg_s_buf[0] << "," << ecg_m_buf[0] <<"\n";

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
    // Datalogging
    for(int i=0; i<10000; i++){
        outfile << ekg[i].x << "," << ekg[i].y << "," << ecg_m[i] <<  "," << is_peak[i] <<"\n";
    }
    outfile.close();
    int count=0;

    for (int n = 0; n < peak_i_vec.size(); n++)
    {
         if(peak_i_vec[n] < 80){
             count++;
         }
    }

    peak_i_vec.erase(peak_i_vec.begin(), peak_i_vec.begin() + count);
    peak_vec.erase(peak_vec.begin(), peak_vec.begin()+count);
    
    // kmeans Algorithm
    kmeans(peak_vec, peak_vec.size());

    return 0;

}

int main(){
    // training data
    training("data/data10/data10_abd1.csv");
    // load data
    readcsv("data/data10/data10_abd1.csv");

    // buffer
    double ecg_buf[len_buf] = {0};
    double ecg_f_buf[len_buf] = {0};
    double ecg_d_buf[len_buf] = {0};
    double ecg_s_buf[len_buf] = {0};
    double ecg_m_buf0[len_buf] = {0};
    double ecg_m_buf[len_buf] = {0};

    // container
    double ecg_m[60000];

    // find peaks parameter
    double is_peak[60000] = {0};
    double peaks;
    int peaks_i;

    // Peak container
    std::vector<double> peak_vec;
    std::vector<int> peak_i_vec;

    // HR container
    double mHR = 0, fHR = 0, mRRavr = 0, fRRavr = 500;
    double mRR[9], fRR[9];
    std::vector<double> mQrs;
    std::vector<double> fQrs;
    std::vector<double> noisePeak;

    // Datalogging
    std::ofstream outfile4("data/data10/out/data10_abd1_out4_10s.csv");

    for(int i=0; i<60000; i++){
        ecg_buf[0] = ekg[i].y;
        ecg_f_buf[0] = filt(ecg_buf, ecg_f_buf, len_b_b, b_b, a_b);
        ecg_d_buf[0] = filt(ecg_f_buf, ecg_d_buf, len_b_d, b_d, a_d)/1000;
        ecg_s_buf[0] = ecg_d_buf[0]*ecg_d_buf[0];
        ecg_m_buf0[0] = filt(ecg_s_buf, ecg_m_buf0, len_b_m, b_m, a_m);
        ecg_m_buf[0] = filt(ecg_m_buf0, ecg_m_buf, len_b_m, b_m, a_m);
        ecg_m[i] = ecg_m_buf[0];
        
        if(ecg_m_buf[1] > ecg_m_buf[2] && ecg_m_buf[1] >= ecg_m_buf[0]){
            peaks = ecg_m_buf[1];
            peaks_i = i - 1;
            is_peak[i-1] = peaks;
            peak_vec.push_back(peaks);
            peak_i_vec.push_back(peaks_i);

            // detect QRS
            if(abs(peaks - centroid[0]) < abs(peaks - centroid[1]) && 
            abs(peaks - centroid[0]) < abs(peaks - centroid[2])){
                noisePeak.push_back(peaks_i);
                centroid[0] = (centroid[0]+peaks)/2;
                // std::cout << "noise peak:" << peaks_i << '\n';
            }else if (abs(peaks - centroid[1]) < abs(peaks - centroid[0]) && 
            abs(peaks - centroid[1]) < abs(peaks - centroid[2])){
                fQrs.push_back(peaks_i);

                if(fQrs.size() >= 2){
                    fRR[0] = fQrs.end()[-1]-fQrs.end()[-2];
                    // Search Back
                    if(fRR[0] >= 1.66*fRRavr && fRRavr != 0){
                        if(fQrs.end()[-1] - mQrs.end()[-1] >= 0.82*fRRavr && 
                        fQrs.end()[-1] - mQrs.end()[-1] <= 1.26*fRRavr && mQrs.size() != 0){
                            fQrs.push_back(peaks_i);
                            fQrs.end()[-2] = mQrs.end()[-1];
                            fRR[0] = fQrs.end()[-1]-fQrs.end()[-2];
                        }else{
                            for(int p=1;p<=noisePeak.size();p++){
                                if (noisePeak.end()[-p] < fQrs.end()[-2]){
                                    break;
                                }
                                
                                if(fQrs.end()[-1] - noisePeak.end()[-p] >= 0.82*fRRavr && 
                                fQrs.end()[-1] - noisePeak.end()[-p] <= 1.26*fRRavr && noisePeak.size() != 0){
                                    fQrs.push_back(peaks_i);
                                    fQrs.end()[-2] = noisePeak.end()[-p];
                                    fRR[0] = fQrs.end()[-1]-fQrs.end()[-2];
                                    centroid[0] = centroid[0]/2;
                                    break;
                                }
                            }
                        }
                    }else if(peaks< 1.66*centroid[2]){
                        centroid[1] = (centroid[1]+peaks)/2;
                    }
                    
                    fHR = 60/fRR[0] * 1000000/fs ;
                    int fCount=1;
                    fRRavr = 500;
                    for (int m = 8; m >= 0; m--){
                        fRR[m+1] = fRR[m];
                        if(fRR[m+1] != 0){
                            fCount++;
                            fRRavr += fRR[m+1];
                        }
                    }
                    if(fCount != 0){
                        fRRavr = fRRavr/fCount;
                    }else{
                        fRRavr = 500;
                    }
                }
                std::cout << "fHR, " << peaks_i << ", " << fHR << ", " << fRRavr << '\n';
                
            }else{
                mQrs.push_back(peaks_i);

                if(mQrs.size() >= 2){
                    mRR[0] = mQrs.end()[-1]-mQrs.end()[-2];
                    // Search Back
                    if(mRR[0] >= 1.66*mRRavr && mRRavr != 0){
                        for(int p=1;p<=fQrs.size();p++){
                            if((mQrs.end()[-1] - fQrs.end()[-p]) >= 0.92*mRRavr && 
                            (mQrs.end()[-1] - fQrs.end()[-p]) <= 1.16*mRRavr && fQrs.size() != 0){
                                mQrs.push_back(peaks_i);
                                mQrs.end()[-2] = fQrs.end()[-p];
                                mRR[0] = mQrs.end()[-1]-mQrs.end()[-2];
                                centroid[1] = centroid[1]/2;
                                break;
                            }
                        }
                    }else if(peaks< 1.66*centroid[2]){
                        centroid[2] = (centroid[2]+peaks)/2;
                    }
                    if(mRR[0]!=0){
                        mHR = 60/mRR[0] * 1000000/fs ;
                    }else{
                        mHR = 0;
                    }
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
                    }else{
                        mRRavr = 85;
                    }
                }
                std::cout << "mHR, " << peaks_i << ", " << mHR << ", " << mRRavr << '\n';
            }
        }
        
        outfile4 << ekg[i].x << "," << ecg_buf[0] << "," << ecg_f_buf[0] << "," << ecg_d_buf[0] << "," <<
            ecg_s_buf[0] << "," << ecg_m_buf[0] <<"\n";

        for(int m = len_buf-2; m >= 0; m--){
            ecg_buf[m+1] = ecg_buf[m];
            ecg_f_buf[m+1] = ecg_f_buf[m];
            ecg_d_buf[m+1] = ecg_d_buf[m];
            ecg_s_buf[m+1] = ecg_s_buf[m];
            ecg_m_buf0[m+1] = ecg_m_buf0[m];
            ecg_m_buf[m+1] = ecg_m_buf[m];
        }
    }
    outfile4.close();
    // Datalogging
    std::ofstream outfile3("data/data10/out/data10_abd1_out3_10s.csv");
    for (int i = 0; i<fQrs.size(); i++){
        outfile3 << centroid[1] << "," << fQrs[i] << "\n";
    }
    outfile3.close();
    return 0;

}
