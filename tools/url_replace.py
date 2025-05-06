from collections.abc import Generator
from typing import Any
import re
import io

from dify_plugin import File, Tool
from dify_plugin.file.file import File
from dify_plugin.entities.tool import ToolInvokeMessage

class UrlReplaceTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        file = tool_parameters.get("txt_file")  # 注意参数名要与yaml定义一致
        prefix = tool_parameters.get("prefix")
        suffix = tool_parameters.get("suffix")
        
        try:
            # 验证文件类型
            if not isinstance(file, File):
                yield self.create_text_message("无效的文件输入")
                return
                
            # 获取文件内容和文件名
            try:
                file_content = file.blob.decode('utf-8')  # 直接从blob解码
                if not file_content.strip():  # 检查内容是否为空
                    yield self.create_text_message("文件内容为空")
                    return
                    
            except UnicodeDecodeError:
                yield self.create_text_message("文件编码错误，请使用UTF-8编码的文本文件")
                return
                
            original_filename = file.filename or "document.txt"
            
            # 执行URL替换（内存操作）
            pattern = re.compile(r'url(\d+)')
            new_content = pattern.sub(
                lambda m: f"{prefix}url{m.group(1)}.{suffix}", 
                file_content
            )
            
            # 返回处理后的文件（内存操作）
            yield self.create_blob_message(
                blob=new_content.encode('utf-8'),
                meta={
                    "mime_type": "text/plain",
                    "file_name": f"【处理】{original_filename}"
                }
            )
            
        except UnicodeDecodeError:
            yield self.create_text_message("文件编码错误，请使用UTF-8编码的文本文件")
        except Exception as e:
            yield self.create_text_message(f"处理错误: {str(e)}")