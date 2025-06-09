import os
import sys
from http import HTTPStatus
import dashscope
from dashscope import Generation
# export DASHSCOPE_API_KEY='YOUR-DASHSCOPE-API-KEY' in environment
def sync_dashscope_sample():
    responses = Generation.call(
        model=Generation.Models.qwen_plus,
        prompt='Is the API connection working?',
        temperature=0.1,)

    if responses.status_code == HTTPStatus.OK:
        print('Result is: %s'%responses.output.text)
    else:
        print('Code: %s, status_code: %s, code: %s, message: %s'%(responses.status_code,
                                                   responses.code,
                                                   responses.message))

if __name__ == '__main__':
    dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")
    if not dashscope.api_key:
        print("Error: DASHSCOPE_API_KEY environment variable is not set.")
        sys.exit(1)
    sync_dashscope_sample()