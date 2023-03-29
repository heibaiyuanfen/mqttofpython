#include "face.h"
#include <iostream>
#include <string>
#include <stdio.h>
#include <regex>
#include <sstream>
#include <fstream>
#include <iterator>
#include <thread>
#include "opencv2/opencv.hpp"
#include <chrono>
#include <sys/time.h>
#include "face_demo.h"
#include "base64.h"

// 鑾峰彇鏃堕棿鎴?
std::time_t get_timestamp() {
    std::chrono::time_point <std::chrono::system_clock, std::chrono::milliseconds> tp = std::chrono::time_point_cast<std::chrono::milliseconds>(
            std::chrono::system_clock::now());
    auto tmp = std::chrono::duration_cast<std::chrono::milliseconds>(tp.time_since_epoch());
    std::time_t timestamp = tmp.count();
    return timestamp;
}


int face_sdk_init() {
    std::string model_path = "/usr/local/face_sdk";
    int res = api->sdk_init(model_path.c_str());
    return res;
}

void destroy_sdk() {
    delete api;
}

cv::Mat base2mat(std::string &base64_data) {
    cv::Mat img;
    std::string s_mat;
    s_mat = base64_decode(base64_data.data(), false);
    std::vector<char> base64_img(s_mat.begin(), s_mat.end());
    img = cv::imdecode(base64_img, cv::IMREAD_COLOR); //CV::IMREAD_UNCHANGED
    return img;
}

char *user_add(const char *user_id, const char *group_id, const char *base64) {
    std::string str = base64;
    cv::Mat mat = base2mat(str);
    std::vector <Feature> fea_list;
    std::vector <FaceBox> box_list;
    std::string user_info = "";
    //浜鸿劯娉ㄥ唽杩斿洖json
    std::string res;
    char *tmp = new char[256];
    api->user_add(res, &mat, user_id, group_id, user_info.c_str());
    strcpy(tmp, res.c_str());
    return tmp;

}

char *user_update(const char *user_id, const char *group_id, const char *base64) {
    std::string str = base64;
    cv::Mat mat = base2mat(str);
    std::vector <Feature> fea_list;
    std::vector <FaceBox> box_list;
    std::string user_info = "";

    // type 0锛?琛ㄧずrgb 浜鸿劯妫€娴?1锛氳〃绀簄ir浜鸿劯妫€娴?    
    int type = 0;
    // 鎻愬彇鍒颁汉鑴哥壒寰佸€?   
     if (!mat.empty()) {
        //浜鸿劯鏇存柊杩斿洖json
        std::string res;
        char *tmp = new char[256];
        api->user_update(res, &mat, user_id, group_id, user_info.c_str());
        strcpy(tmp, res.c_str());
        return tmp;
    } else {
//        return "{"
//               "\"errno\" : -1000,\n"
//               "\"msg\" : \"image has no face or image not exist\"\n"
//               "}";
        return "{\"data\": {\"log_id\": \"0\"}, \"errno\": -1000, \"msg\": \"image has no face or image not exist\"}";
    }
}

char *user_delete(const char *user_id, const char *group_id) {
    std::string res;
    char *tmp = new char[256];
    api->user_delete(res, user_id, group_id);
    strcpy(tmp, res.c_str());
    return tmp;
}

char *group_add(const char *group_id) {
    std::string res;
    char *tmp = new char[256];
    api->group_add(res, group_id);
    strcpy(tmp, res.c_str());
    return tmp;
}

char *group_delete(const char *group_id) {
    std::string res;
    char *tmp = new char[256];
    api->group_delete(res, group_id);
    strcpy(tmp, res.c_str());
    return tmp;
}

char *identify(const char *group_id, const char *base64) {
    // type 0锛?琛ㄧずrgb 浜鸿劯妫€娴?1锛氳〃绀簄ir浜鸿劯妫€娴?    
    int type = 0;
    std::string str = base64;
    cv::Mat mat = base2mat(str);
    // 鍜屼汉鑴稿簱閲岄潰鐨勭壒寰佸€艰繘琛屾瘮杈冿紝浜鸿劯搴撳彲鍙傝€僨ace_manager.cpp
    std::string user_id = "";
    std::string res;
    api->identify(res, &mat, group_id, user_id.c_str(), type);
    char *tmp = new char[4096];
    strcpy(tmp, res.c_str());
    return tmp;
}

char *identify_with_all(const char *base64) {
    // type 0锛?琛ㄧずrgb 浜鸿劯妫€娴?1锛氳〃绀簄ir浜鸿劯妫€娴?   
     int type = 0;
    std::string str = base64;
    cv::Mat mat = base2mat(str);
    // 鍜屼汉鑴稿簱閲岄潰鐨勭壒寰佸€艰繘琛屾瘮杈冿紝浜鸿劯搴撳彲鍙傝€僨ace_manager.cpp
    std::string user_id = "";
    std::string res;
    api->load_db_face();
    api->identify_with_all(res, &mat, type);
    char *tmp = new char[4096];
    strcpy(tmp, res.c_str());
    return tmp;
}

char *get_device_id() {
    std::string res;
    api->get_device_id(res);
    char *tmp = new char[128];
    strcpy(tmp, res.c_str());
    return tmp;
}

*/
Face::Face() {
}

Face::~Face() {
}
