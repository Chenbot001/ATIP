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
    dashscope.api_key = 'sk-cc3a2097a12e4c22a3c72e57ffd0b3bb'
    sync_dashscope_sample()