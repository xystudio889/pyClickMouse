import markdown

if __name__ == '__main__':
    file = input("请输入markdown文件路径: ")
    with open(file, 'r', encoding='utf-8') as f:
        md_text = f.read()
    html_text = markdown.markdown(md_text)
    with open('output.html', 'w', encoding='utf-8') as f:
        f.write(html_text)
    print("转换完成！位于output.html文件中。")