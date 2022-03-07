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

struct point ekg[10000];
int fs = 1000;
const int len_buf = 0.09 * fs;

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


int kmeans(std::vector<double> X, int len_X, int max_iter = 300, double tol = 0.0001){
    int n_cluster = 3;
    double centroid[n_cluster];
    bool diff = true;
    std::vector<double> k1, k2, k3;
    int iter=0;
    int label[len_X] = {0};
    // init centroid
    double upper_bound = *std::max_element(X.begin(), X.end());
    centroid[0] = 0.0;
    centroid[1] = 0.08 * upper_bound;
    centroid[2] = 0.8 * upper_bound;
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
        double avr1 = std::accumulate(k1.begin(), k1.end(), 0.0)/k1.size();
        double avr2 = std::accumulate(k2.begin(), k2.end(), 0.0)/k2.size();
        double avr3 = std::accumulate(k3.begin(), k3.end(), 0.0)/k3.size();
        double new_centroid[] = {avr1, avr2, avr3};
        if(abs(new_centroid[0]-centroid[0]) <= tol && abs(new_centroid[1]-centroid[1]) <= tol 
        && abs(new_centroid[2]-centroid[2]) <= tol){
            diff = false;
        }
        std::cout<<"iter: "<< iter << ", " << centroid[0]<< ", " 
            << centroid[1] << ", " << centroid[2] <<'\n';
        k1.clear();
        k2.clear();
        k3.clear();
        centroid[0] = new_centroid[0];
        centroid[1] = new_centroid[1];
        centroid[2] = new_centroid[2];
        iter++;
    }
    for(int m = 0; m < len_X; m++){
        std::cout<< m << ", " << label[m] << '\n';
    }
    return 0;
}


int main(){
    readcsv("data4.csv");
    // Bandpass filter parameter
    double b_b[] = {0.00295827, 0.0, -0.00591654, 0.0, 0.00295827};
    double a_b[] = {1.0, -3.82193348, 5.49756255, -3.52773632, 0.85219225};
    int len_b_b = sizeof(b_b)/sizeof(b_b[0]);

    // Derivative filter parameter
    double b_d[] = {1.0, 2.0, 0.0, -2.0, -1.0};
    int len_b_d = sizeof(b_d)/sizeof(b_d[0]);
    double a_d[len_b_d] = {0};
    for(int m=0; m < len_b_d; m++){
        b_d[m] = b_d[m]*fs/8;
    }
    // Moving average filter parameter
    int window_width = 60;
    double b_m[window_width];
    int len_b_m = sizeof(b_m)/sizeof(b_m[0]);
    double a_m[len_b_m] = {0};
    for(int m=0; m < len_b_m; m++){
        b_m[m] = 1.0/window_width;
    }
    // buffer
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
    int peak_len = len_buf;
    double peaks;
    int peaks_i;
    int distance = 0;

    // Peak container
    std::vector<double> peak_vec;
    std::vector<int> peak_i_vec;

    // Datalogging
    std::ofstream outfile("data4out.csv");

    for(int i=0; i<10000; i++){
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

        }
        
        // outfile << ekg[i].x << "," << ecg_buf[0] << "," << ecg_f_buf[0] << "," << ecg_d_buf[0] << "," <<
        //     ecg_s_buf[0] << "," << ecg_m_buf[0] <<"\n";

        for(int m = len_buf-2; m >= 0; m--){
            ecg_buf[m+1] = ecg_buf[m];
            ecg_f_buf[m+1] = ecg_f_buf[m];
            ecg_d_buf[m+1] = ecg_d_buf[m];
            ecg_s_buf[m+1] = ecg_s_buf[m];
            ecg_m_buf0[m+1] = ecg_m_buf0[m];
            ecg_m_buf[m+1] = ecg_m_buf[m];
        }
    }
    for(int i=0; i<10000; i++){
        outfile << ekg[i].x << "," << ekg[i].y << "," << ecg_m[i] <<  "," << is_peak[i] <<"\n";
    }
    kmeans(peak_vec, peak_vec.size());
    outfile.close();
    return 0;

}
//// find peaks
// if(i >= peak_len){
//     peaks = *std::max_element(ecg_m_buf, ecg_m_buf+len_buf);
//     auto itr = std::find(std::begin(ecg_m), std::end(ecg_m), peaks);
//     if(itr != std::end(ecg_m)){
//         peaks_i[0] = std::distance(ecg_m, itr);
//         if(peaks_i[0] != peaks_i[1] && peaks_i[0] != peak_len && ecg_m[peaks_i[0]] >= ecg_m[peaks_i[0]-1]){
//             if(peaks_i[0] - peaks_i[1] < 45 ){
//                 if(ecg_m[peaks_i[0]] > ecg_m[peaks_i[1]]){
//                     is_peak[peaks_i[1]] = 0;
//                     is_peak[peaks_i[0]] = peaks;
//                     peak_vec.push_back(peaks);
//                     peak_i_vec.push_back(peaks_i[0]);
//                     // peak_vec.erase(peak_vec.end()-2);
//                     // peak_i_vec.erase(peak_i_vec.end()-2);
//                     peaks_i[1] = peaks_i[2];
//                     // std::cout << peaks_i[0] << "under limit but larger" << '\n';
//                 }
//             }else{
//                 is_peak[peaks_i[0]] = peaks;
//                 peak_vec.push_back(peaks);
//                 peak_i_vec.push_back(peaks_i[0]);
//                 // std::cout << peaks_i[0] << '\n';
//             }
//         }
//         peaks_i[1] = peaks_i[0];
//         peaks_i[2] = peaks_i[1];
//     }
//     peak_len += len_buf/2;
// }
