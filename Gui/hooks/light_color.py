import colorsys

def lighten_color_hex(hex_color, factor):
    '''
    使用HSL色彩空间提亮颜色
    hex_color: 十六进制颜色字符串，如 '#808080'
    factor: 提亮因子 (0-1之间)，0为不变，1为最亮
    '''
    
    if not hex_color.startswith('#') or len(hex_color) != 7:
        raise ValueError('Please enter a valid hex color string, such as #FF0000.')
    
    if not -1 <= factor <= 1:
        raise ValueError('The lightening factor must be between -1 and 1.')
    
    # 移除#号并转换为RGB
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    
    # 转换为HSL
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    
    if factor >= 0:
        # 提亮：向白色(1.0)移动
        l = l + (1.0 - l) * factor
    else:
        # 变暗：向黑色(0.0)移动
        factor_abs = abs(factor)  # 取绝对值
        l = l * (1.0 - factor_abs)
    
    # 转回RGB
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    
    # 转换回十六进制
    hex_result = '#{:02x}{:02x}{:02x}'.format(
        int(r * 255), 
        int(g * 255), 
        int(b * 255)
    )
    
    return hex_result

# 测试函数
if __name__ == '__main__':
    # 交互式测试
    while True:
        try:
            user_color = input('输入一个十六进制颜色(如#808080)，或输入"q"退出: ').strip()
            
            if user_color.lower() == 'q':
                print('退出程序')
                break
            
            user_factor = float(input('输入提亮因子 (0-1，如0.3表示30%): ').strip())
            
            result = lighten_color_hex(user_color, user_factor)
            
            print(f'\n原始颜色: {user_color}')
            print(f'提亮后:   {result} (提亮 {int(user_factor*100)}%)')
            
        except ValueError:
            print('输入无效，请重新输入')
        except KeyboardInterrupt:
            print('\n程序被中断')
            break