import os
import re
import requests
import subprocess
import urllib.parse
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from flask import Flask, request, render_template, redirect, url_for, flash, session


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 应用程序的密钥
PASSWORD = 'your_PASSWORD'  # 设置密码

def clean_filename(filename):
    """清理文件名，移除非法字符"""
    return re.sub(r'[<>:"/\\|?*]', '', filename)

#--------------------------------------------------------------------

def allpicture(url, save_dir='images'):
    """下载网页上的所有图片"""
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find_all('img')

        for index, img in enumerate(images):
            img_url = img.get('src')
            if img_url:
                img_url = urljoin(url, img_url)
                img_extension = os.path.splitext(img_url)[1].lower()

                if img_extension not in ['.jpg', '.jpeg', '.png', '.gif']:
                    continue

                img_name = f'image_{index+1}{img_extension}'
                img_name = clean_filename(img_name)
                img_path = os.path.join(save_dir, img_name)

                try:
                    img_response = requests.get(img_url, headers=headers, stream=True, timeout=10)
                    img_response.raise_for_status()

                    with open(img_path, 'wb') as file:
                        for chunk in img_response.iter_content(chunk_size=8192):
                            file.write(chunk)

                except requests.RequestException as e:
                    print(f"下载图片 {img_url} 时出错: {e}")

    except requests.RequestException as e:
        print(f"请求错误: {e}")

def wgetzip(url, save_dir='images'):
    """下载指定 URL 的文件"""
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        decoded_url = urllib.parse.unquote(url)
        response = requests.get(decoded_url, headers=headers, stream=True, timeout=10)
        response.raise_for_status()

        filename = os.path.basename(decoded_url)
        if not filename:
            filename = 'file.zip'

        filename = clean_filename(filename)
        file_path = os.path.join(save_dir, filename)

        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        print(f"文件已成功下载到 {file_path}")

    except requests.RequestException as e:
        print(f"下载文件 {url} 时出错: {e}")
    except OSError as e:
        print(f"文件系统错误: {e}")
        
#mega
    
def download_mega_file(mega_url, save_dir='images'):
    """从 Mega.nz 下载文件并保存到 images 目录"""
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    try:
        # 使用 megadl 命令下载文件到指定目录
        result = subprocess.run(['megadl', '--path', save_dir, mega_url], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("文件已成功下载")
        else:
            print(f"下载文件时出错: {result.stderr}")
    
    except Exception as e:
        print(f"下载文件时发生错误: {e}")

#index.html
#--------------------------------------------------------------------

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # 密码验证
        password = request.form.get('password')
        if password != PASSWORD:
            flash('密码错误!')
            return redirect(url_for('index'))

        url = request.form.get('url')
        option = request.form.get('option')
        
        if not url:
            flash('URL 是必填项!')
            return redirect(url_for('index'))

#def
#---------------------------
        if option == 'allpicture':
            allpicture(url)
        elif option == 'wgetzip':
            wgetzip(url)
        elif option == 'megafile':
            download_mega_file(url)
        else:
            flash('选择的选项无效!')
            return redirect(url_for('index'))
#---------------------------

        flash('操作已成功完成!')
        return redirect(url_for('index'))

    return render_template('index.html')

@app.route('/folder_size', methods=['GET'])
def folder_size():
    folder = 'images'
    if not os.path.exists(folder):
        return '已下载完成', 200
        
    total_size = sum(os.path.getsize(os.path.join(root, file)) for root, dirs, files in os.walk(folder) for file in files)
    return f'当前下载： {total_size / (1024 * 1024):.2f} MB', 200

if __name__ == '__main__':
    app.run(debug=True)
