void appendFile(fs::FS &fs, const char * path, const char * message) {
  File file = fs.open(path, FILE_APPEND);
  if (!file)
  {
    log_i("Failed to open file for appending");
    return;
  } else {
    file.print(message);
    file.close();
  }
}

void SDWriteStart(){
  // create new file by opening file for writing
  fileName = "/meas_0.txt";
  int count = 0;
  while(SD.exists(fileName.c_str())){
    count++;
    fileName = String("/meas_") + count + String(".txt");
  }
  appendFile(SD, fileName.c_str(), "[");
}

void SDWriteEnd(){
  appendFile(SD, fileName.c_str(), "]");
}