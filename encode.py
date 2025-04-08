from Crypto.Cipher import AES
import base64

# 默认的密钥和IV（初始化向量）
default_key = "1234567890123456".encode('utf-8')
default_iv = "1234567890123456".encode('utf-8')


# 自定义零填充函数
def zero_pad(data, block_size):
    padding_len = block_size - len(data) % block_size
    return data + bytes([0] * padding_len)


def R(e, t=None, r=None):
    # 如果提供了t和r，则使用它们作为密钥和IV
    key = default_key if t is None else t.encode('utf-8')
    iv = default_iv if r is None else r.encode('utf-8')

    # 要加密的消息
    message = e.encode('utf-8')

    # 对消息进行零填充，以确保其长度是块大小的整数倍
    padded_message = zero_pad(message, AES.block_size)

    # 创建一个AES cipher对象，使用CBC模式
    cipher = AES.new(key, AES.MODE_CBC, iv)

    # 加密填充后的消息
    encrypted = cipher.encrypt(padded_message)

    # 将加密后的字节串编码为Base64字符串
    base64_encrypted = base64.b64encode(encrypted)

    return base64_encrypted.decode('utf-8')


def run_encode(passwords):
    e = passwords
    # 使用默认密钥和IV
    encrypted_message = R(e)
    return encrypted_message



