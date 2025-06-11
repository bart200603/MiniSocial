from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from datetime import datetime
import os
import uuid
import hashlib
import json
import random
import string
from werkzeug.utils import secure_filename

app = Flask(__name__, 
           template_folder='templates',
           static_folder='static')
app.secret_key = os.environ.get('SECRET_KEY') or 'minisocial_secret_key_change_in_production'  # 用于session加密
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 会话过期时间：1天

# 文件上传配置
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB 最大文件大小
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# 数据存储（实际项目中应使用数据库）
DATA_FILE = 'data.json'

def load_data():
    """加载数据文件"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            app.logger.error(f"加载数据文件出错: {e}")
            return create_empty_data()
    else:
        return create_empty_data()

def create_empty_data():
    """创建空数据结构"""
    return {
        'users': {},
        'posts': [],
        'comments': [],
        'likes': [],
        'follows': []
    }

def save_data(data):
    """保存数据到文件"""
    try:
        # 在Vercel环境中，我们需要检查是否有写入权限
        if os.environ.get('VERCEL') == '1':
            # 在Vercel中，我们只能在/tmp目录写入
            tmp_file = '/tmp/data.json'
            with open(tmp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            # 注意：这个文件在函数执行结束后会消失
            # 在实际生产环境中，应该使用数据库或外部存储服务
        else:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        app.logger.error(f"保存数据文件出错: {e}")

# 初始化数据
data = load_data()

def hash_password(password):
    """更安全的密码哈希（使用盐值）"""
    # 在实际项目中应使用 bcrypt 或 Argon2
    salt = os.urandom(32)  # 32字节的随机盐
    key = hashlib.pbkdf2_hmac(
        'sha256',  # 使用的哈希函数
        password.encode('utf-8'),  # 转换为字节
        salt,  # 盐值
        100000,  # 迭代次数
        dklen=128  # 结果长度
    )
    # 存储盐和密钥
    return salt.hex() + ':' + key.hex()

def verify_password(stored_password, provided_password):
    """验证密码"""
    # 分离存储的盐和密钥
    salt_hex, key_hex = stored_password.split(':')
    salt = bytes.fromhex(salt_hex)
    stored_key = bytes.fromhex(key_hex)
    
    # 使用相同的盐和算法计算提供密码的哈希
    key = hashlib.pbkdf2_hmac(
        'sha256',
        provided_password.encode('utf-8'),
        salt,
        100000,
        dklen=128
    )
    
    # 安全比较
    return key == stored_key

def allowed_file(filename):
    """检查文件类型是否允许上传"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_image(file):
    """验证图片文件"""
    # 检查文件大小
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > MAX_CONTENT_LENGTH:
        return False, "文件大小超过限制"
    
    # 检查文件扩展名
    if not allowed_file(file.filename):
        return False, "不支持的文件类型"
    
    # 这里可以添加更多的验证，如检查文件内容
    
    return True, "验证通过"

def get_current_user():
    """获取当前登录用户信息"""
    if 'user_id' in session:
        user_id = session['user_id']
        if user_id in data['users']:
            return data['users'][user_id]
    return None

def generate_captcha(length=4):
    """生成随机验证码"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def save_uploaded_file(file, filename):
    """保存上传的文件，适应Vercel环境"""
    if os.environ.get('VERCEL') == '1':
        # 在Vercel中，我们只能在/tmp目录写入
        # 但这些文件会在函数执行结束后消失
        # 在实际生产环境中，应该使用外部存储服务如S3
        tmp_path = os.path.join('/tmp', filename)
        file.save(tmp_path)
        # 注意：这个文件在函数执行结束后会消失
        return os.path.join(app.config['UPLOAD_FOLDER'], filename)
    else:
        # 本地开发环境
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return file_path

@app.route('/')
def index():
    """主页"""
    user = get_current_user()
    posts = sorted(data['posts'], key=lambda x: x['timestamp'], reverse=True)
    
    # 获取每个帖子的评论和点赞
    for post in posts:
        post['comments'] = [c for c in data['comments'] if c['post_id'] == post['id']]
        post['likes_count'] = len([l for l in data['likes'] if l['post_id'] == post['id']])
        
        # 获取作者信息
        if post['user_id'] in data['users']:
            post['author'] = data['users'][post['user_id']]['username']
            post['avatar'] = data['users'][post['user_id']].get('avatar', 'static/images/default_avatar.txt')
    
    return render_template('index.html', user=user, posts=posts, data=data)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        captcha = request.form.get('captcha')
        
        # 验证验证码
        if 'captcha' not in session or session['captcha'] != captcha:
            flash('验证码错误')
            return redirect(url_for('register'))
        
        # 验证用户名是否已存在
        for user in data['users'].values():
            if user['username'] == username:
                flash('用户名已存在')
                return redirect(url_for('register'))
        
        # 创建新用户
        user_id = str(uuid.uuid4())
        data['users'][user_id] = {
            'id': user_id,
            'username': username,
            'password': hash_password(password),
            'email': email,
            'bio': '',
            'avatar': 'static/images/default_avatar.txt',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        save_data(data)
        
        # 自动登录
        session['user_id'] = user_id
        flash('注册成功')
        return redirect(url_for('index'))
    
    # 生成验证码
    captcha = generate_captcha()
    session['captcha'] = captcha
        
    return render_template('register.html', captcha=captcha)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # 验证用户名和密码
        for user_id, user in data['users'].items():
            if user['username'] == username:
                # 处理旧密码格式
                if ':' not in user['password']:
                    # 旧格式密码，直接比较哈希值
                    if user['password'] == hashlib.sha256(password.encode()).hexdigest():
                        # 更新为新格式密码
                        user['password'] = hash_password(password)
                        save_data(data)
                        session['user_id'] = user_id
                        flash('登录成功')
                        return redirect(url_for('index'))
                # 新格式密码，使用安全验证
                elif verify_password(user['password'], password):
                    session['user_id'] = user_id
                    flash('登录成功')
                    return redirect(url_for('index'))
        
        flash('用户名或密码错误')
        return redirect(url_for('login'))
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    """用户登出"""
    session.pop('user_id', None)
    flash('已退出登录')
    return redirect(url_for('index'))

@app.route('/profile/<user_id>')
def profile(user_id):
    """用户个人资料页"""
    if user_id not in data['users']:
        flash('用户不存在')
        return redirect(url_for('index'))
    
    user = data['users'][user_id]
    current_user = get_current_user()
    
    # 获取用户的帖子
    user_posts = [p for p in data['posts'] if p['user_id'] == user_id]
    user_posts = sorted(user_posts, key=lambda x: x['timestamp'], reverse=True)
    
    # 获取关注信息
    followers = [f for f in data['follows'] if f['following_id'] == user_id]
    following = [f for f in data['follows'] if f['follower_id'] == user_id]
    
    # 检查当前用户是否已关注该用户
    is_following = False
    if current_user:
        is_following = any(f['follower_id'] == current_user['id'] and f['following_id'] == user_id for f in data['follows'])
    
    return render_template('profile.html', 
                           user=user, 
                           posts=user_posts, 
                           followers_count=len(followers), 
                           following_count=len(following),
                           is_following=is_following,
                           current_user=current_user,
                           comments=data['comments'],
                           likes=data['likes'],
                           users=data['users'])

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    """编辑个人资料"""
    user = get_current_user()
    if not user:
        flash('请先登录')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        bio = request.form.get('bio', '')
        
        # 处理头像上传
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename != '':
                # 验证图片
                is_valid, message = validate_image(file)
                if not is_valid:
                    flash(message)
                    return redirect(url_for('edit_profile'))
                
                filename = secure_filename(file.filename)
                # 使用用户ID作为文件名前缀避免冲突
                filename = f"{user['id']}_{filename}"
                
                try:
                    file_path = save_uploaded_file(file, filename)
                    user['avatar'] = file_path
                except Exception as e:
                    app.logger.error(f"保存文件失败: {e}")
                    flash('头像上传失败')
                    return redirect(url_for('edit_profile'))
        
        user['bio'] = bio
        save_data(data)
        flash('个人资料已更新')
        return redirect(url_for('profile', user_id=user['id']))
        
    return render_template('edit_profile.html', user=user)

@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
    """创建新帖子"""
    user = get_current_user()
    if not user:
        flash('请先登录')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        content = request.form.get('content', '')
        
        if not content.strip():
            flash('内容不能为空')
            return redirect(url_for('create_post'))
        
        # 处理图片上传
        image_url = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                # 验证图片
                is_valid, message = validate_image(file)
                if not is_valid:
                    flash(message)
                    return redirect(url_for('create_post'))
                
                filename = secure_filename(file.filename)
                # 使用时间戳和用户ID作为文件名前缀避免冲突
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                filename = f"{user['id']}_{timestamp}_{filename}"
                
                try:
                    file_path = save_uploaded_file(file, filename)
                    image_url = file_path
                except Exception as e:
                    app.logger.error(f"保存文件失败: {e}")
                    flash('图片上传失败')
                    return redirect(url_for('create_post'))
        
        # 创建帖子
        post_id = str(uuid.uuid4())
        post = {
            'id': post_id,
            'user_id': user['id'],
            'content': content,
            'image_url': image_url,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        data['posts'].append(post)
        save_data(data)
        
        flash('帖子发布成功')
        return redirect(url_for('index'))
        
    return render_template('create_post.html', user=user)

@app.route('/follow/<user_id>')
def follow(user_id):
    """关注用户"""
    current_user = get_current_user()
    if not current_user:
        flash('请先登录')
        return redirect(url_for('login'))
    
    if user_id not in data['users']:
        flash('用户不存在')
        return redirect(url_for('index'))
    
    # 不能关注自己
    if current_user['id'] == user_id:
        flash('不能关注自己')
        return redirect(url_for('profile', user_id=user_id))
    
    # 检查是否已关注
    if not any(f['follower_id'] == current_user['id'] and f['following_id'] == user_id for f in data['follows']):
        follow_data = {
            'follower_id': current_user['id'],
            'following_id': user_id,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        data['follows'].append(follow_data)
        save_data(data)
        flash('关注成功')
    
    return redirect(url_for('profile', user_id=user_id))

@app.route('/unfollow/<user_id>')
def unfollow(user_id):
    """取消关注"""
    current_user = get_current_user()
    if not current_user:
        flash('请先登录')
        return redirect(url_for('login'))
    
    # 移除关注关系
    data['follows'] = [f for f in data['follows'] if not (f['follower_id'] == current_user['id'] and f['following_id'] == user_id)]
    save_data(data)
    flash('已取消关注')
    
    return redirect(url_for('profile', user_id=user_id))

@app.route('/like_post/<post_id>')
def like_post(post_id):
    """点赞帖子"""
    user = get_current_user()
    if not user:
        flash('请先登录')
        return redirect(url_for('login'))
    
    # 检查帖子是否存在
    post_exists = any(p['id'] == post_id for p in data['posts'])
    if not post_exists:
        flash('帖子不存在')
        return redirect(url_for('index'))
    
    # 检查是否已点赞
    already_liked = any(l['user_id'] == user['id'] and l['post_id'] == post_id for l in data['likes'])
    
    if already_liked:
        # 取消点赞
        data['likes'] = [l for l in data['likes'] if not (l['user_id'] == user['id'] and l['post_id'] == post_id)]
    else:
        # 添加点赞
        like_data = {
            'user_id': user['id'],
            'post_id': post_id,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        data['likes'].append(like_data)
    
    save_data(data)
    
    # 获取来源页面并返回
    return redirect(request.referrer or url_for('index'))

@app.route('/comment/<post_id>', methods=['POST'])
def add_comment(post_id):
    """添加评论"""
    user = get_current_user()
    if not user:
        flash('请先登录')
        return redirect(url_for('login'))
    
    content = request.form.get('content', '')
    if not content:
        flash('评论不能为空')
        return redirect(request.referrer or url_for('index'))
    
    # 检查帖子是否存在
    post_exists = any(p['id'] == post_id for p in data['posts'])
    if not post_exists:
        flash('帖子不存在')
        return redirect(url_for('index'))
    
    # 添加评论
    comment_id = str(uuid.uuid4())
    comment = {
        'id': comment_id,
        'user_id': user['id'],
        'post_id': post_id,
        'content': content,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    data['comments'].append(comment)
    save_data(data)
    
    flash('评论发布成功')
    return redirect(request.referrer or url_for('index'))

@app.route('/search', methods=['GET'])
def search():
    """搜索用户和帖子"""
    query = request.args.get('q', '')
    user_results = []
    post_results = []
    
    if query:
        # 搜索用户
        for user in data['users'].values():
            if query.lower() in user['username'].lower():
                user_results.append(user)
        
        # 搜索帖子内容
        for post in data['posts']:
            if query.lower() in post['content'].lower():
                # 获取作者信息
                if post['user_id'] in data['users']:
                    post['author'] = data['users'][post['user_id']]['username']
                    post['avatar'] = data['users'][post['user_id']].get('avatar', 'static/images/default_avatar.txt')
                # 获取评论和点赞
                post['comments'] = [c for c in data['comments'] if c['post_id'] == post['id']]
                post['likes_count'] = len([l for l in data['likes'] if l['post_id'] == post['id']])
                post_results.append(post)
    
    return render_template('search_results.html', 
                          user_results=user_results, 
                          post_results=post_results, 
                          query=query, 
                          user=get_current_user(),
                          data=data)

@app.route('/feed')
def feed():
    """关注用户的动态"""
    user = get_current_user()
    if not user:
        flash('请先登录')
        return redirect(url_for('login'))
    
    # 获取当前用户关注的用户ID
    following_ids = [f['following_id'] for f in data['follows'] if f['follower_id'] == user['id']]
    
    # 获取关注用户的帖子
    feed_posts = [p for p in data['posts'] if p['user_id'] in following_ids]
    feed_posts = sorted(feed_posts, key=lambda x: x['timestamp'], reverse=True)
    
    # 获取每个帖子的评论和点赞
    for post in feed_posts:
        post['comments'] = [c for c in data['comments'] if c['post_id'] == post['id']]
        post['likes_count'] = len([l for l in data['likes'] if l['post_id'] == post['id']])
        
        # 获取作者信息
        if post['user_id'] in data['users']:
            post['author'] = data['users'][post['user_id']]['username']
            post['avatar'] = data['users'][post['user_id']].get('avatar', 'static/images/default_avatar.txt')
    
    return render_template('feed.html', user=user, posts=feed_posts, data=data)

# 保留原有的消息墙功能
messages = []

@app.route('/submit', methods=['POST'])
def submit():
    """接收新消息"""
    message = request.form.get('msg')
    if message:
        # 添加时间戳
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        formatted_message = f"[{timestamp}] {message}"
        messages.append(formatted_message)
        print(f"收到新消息: {formatted_message}")
        return "OK"
    return "消息不能为空", 400

@app.route('/messages', methods=['GET'])
def get_messages():
    """获取所有消息"""
    return jsonify(messages)

@app.route('/message_wall')
def message_wall():
    """原始消息墙页面"""
    return render_template('message_wall.html', user=get_current_user())

# 错误处理
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error="页面不存在", code=404), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', error="服务器内部错误", code=500), 500

if __name__ == '__main__':
    # 确保上传目录存在
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    print("MiniSocial服务已启动，访问 http://localhost:5000")
    app.run(debug=True) 