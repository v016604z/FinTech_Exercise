import os
import chardet

class cmpFile:

    def __init__(self, file1, file2):
        self.file1 = file1
        self.file2 = file2

    def fileExists(self):
        return os.path.exists(self.file1) and os.path.exists(self.file2)

    # 自動檢測文件編碼
    def detect_encoding(self, file):
        with open(file, 'rb') as f:
            raw_data = f.read()
        result = chardet.detect(raw_data)
        return result['encoding']

    # 對比文件不同之處，並返回結果
    def compare(self):
        if not self.fileExists():
            return [f"文件 {self.file1} 或 {self.file2} 不存在"]
        
        # 檢測文件的編碼
        encoding1 = self.detect_encoding(self.file1)
        encoding2 = self.detect_encoding(self.file2)

        with open(self.file1, encoding=encoding1) as fp1, open(self.file2, encoding=encoding2) as fp2:
            flist1 = [line for line in fp1]
            flist2 = [line for line in fp2]

        flines1 = len(flist1)
        flines2 = len(flist2)
        if flines1 < flines2:
            flist1.extend([" " * len(flist2[0])] * (flines2 - flines1))
        elif flines2 < flines1:
            flist2.extend([" " * len(flist1[0])] * (flines1 - flines2))

        counter = 1
        cmpreses = []
        for line1, line2 in zip(flist1, flist2):
            if line1 != line2:
                cmpres = f"{self.file1} 和 {self.file2} 第 {counter} 行不同，內容為: {line1.strip()} --> {line2.strip()}"
                cmpreses.append(cmpres)
            counter += 1

        return cmpreses

if __name__ == "__main__":
    cmpfile = cmpFile("outputFile.txt", "rightFile.txt")
    difflines = cmpfile.compare()
    for diff in difflines:
        print(diff)
