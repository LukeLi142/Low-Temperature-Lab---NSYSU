import numpy as np
import re
import os

class DataLoader:
    def __init__(self, inputfile):
        self.inputfile = inputfile
        self.datasets = []

    def Read_ME_File(self):
        """
        讀取txt檔中的數據和分割多組測量資料
        return:
        list[dict] 每個dictionary中就是一組測量數據
        格式為:
        [
            {
                'scan_number':int,
                'data':np.ndarray,
                'downsampling ratio':int,
                'real sampling interval':float
            },
            ...
        ]
        """
        self.datasets = [] # 初始化datasets列表
        current_data = []
        current_downsampling_ratio = None
        current_real_sampling_interval = None

        with open(self.inputfile, "r", encoding = "utf-8", errors = "ignore") as f:
            for raw_line in f:
                line = raw_line.strip() # 去除行首尾的空白字符
                if line.startswith("#####"): # 利用#####來分割數據組
                    if current_data: # 如果current_data不為空，則將其加入到data_list中
                        self.append_dataset(
                            scan_number=len(self.datasets) + 1,
                            data=np.array(current_data),
                            downsampling_ratio = current_downsampling_ratio,
                            real_sampling_interval = current_real_sampling_interval,
                            dt = self.real_sampling_interval * self.downsampling_ratio
                        )
                        
                    current_data = [] # 重置current_data，開始下一組數據的收集
                    current_downsampling_ratio = None
                    current_real_sampling_interval = None

                    continue # 跳過這一行，繼續讀取下一行
                
                elif line.startswith("##"): # 取參數資料
                    lower_line = line.lower() # 將行轉換為小寫以便於比較

                    if "real sampling interval" in lower_line:
                        interval_ns = self._get_value_after_colon(line)
                        self.real_sampling_interval = interval_ns * 1e-9 # 將ns轉換為s
                    elif "downsampling ratio" in lower_line:
                        self.downsampling_ratio = self._get_value_after_colon(line)

                    continue # 跳過這一行，繼續讀取下一行
                
                # 讀取數據行，將其轉換為浮點數並添加到current_data中
                try:
                    value = float(line)
                    current_data.append(value)
                except ValueError:
                    continue # 如果行不能轉換為浮點數，則跳過該行


                # 因為最後一組不會有#####，所以在讀取完文件後需要將最後一組數據加入到datasets中
            if current_data: # 如果current_data不為空，則將其加入到data
                self.append_dataset(
                    scan_number=len(self.datasets) + 1,
                    data=np.array(current_data),
                    downsampling_ratio = current_downsampling_ratio,
                    real_sampling_interval = current_real_sampling_interval,
                    dt = self.real_sampling_interval * self.downsampling_ratio
                )
            return self.datasets
    
    # get voltage from filename
    def get_AC_Vp_voltage_from_filename(self):
        match = re.search(r'HzE([+-]?\d*\.?\d+)V', self.inputfile)
        if match:
            return float(match.group(1))
        else:
            raise ValueError("AC voltage not found in filename.")
    
    # get temperature from filename  
    def get_temperature_from_filename(self):
        match = re.search(r'sampleE(\d+)K', self.inputfile)
        if match:
            return int(match.group(1))
        else:
            raise ValueError("Temperature not found in filename.")

    # 輔助函數
    def append_dataset(self, scan_number, data, downsampling_ratio, real_sampling_interval, dt):
        dataset = {
            'scan_number': scan_number,
            'data': data,
            'downsampling ratio': downsampling_ratio,
            'real sampling interval': real_sampling_interval,
            'dt': dt
        }
        self.datasets.append(dataset)
    
    @staticmethod
    def _get_value_after_colon(line):
        """
        從行中提取冒號後的數值
        """
        parts = line.split(":")
        if len(parts) > 1:
            try:
                return float(parts[1].strip())
            except ValueError:
                raise ValueError(f"Could not convert value to float: {parts[1].strip()}")
        else:
            raise ValueError(f"No colon found in line: {line}")