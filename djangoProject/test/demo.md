1. 查看响应头信息：
	• 响应头通常会包含Content-Type字段，其中包括字符编码信息，例如：
	Content-Type: text/html; charset=ISO-8859-1。
2. 手动设置字符编码：
	• 在解析响应内容时，手动指定字符编码以确保正确解码。例如，使用ISO-8859-1编码：
	import chardet

	raw_content = response.read()
	detected_encoding = chardet.detect(raw_content)['encoding']
	content = raw_content.decode(detected_encoding)
