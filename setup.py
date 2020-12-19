from setuptools import setup, find_packages
import codecs
import os


def read(fname):
    return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()

long_desc = """
    
"""

def read_install_requires():
    reqs = [
            'tushare>=1.2.18'
            ]
    return reqs


setup(
    name='btstock',
    version=read('btstock/VERSION.txt'),
    description='python语言开发，基于tushare的个人股票伺服系统。目标实现策略自动化选股，交易，模型验证，数据分析。',
#     long_description=read("READM.rst"),
    long_description = long_desc,
    author='hxl8489@163.com',
    author_email='hxl8489@163.com',
    license='BSD',
    #url='http://btstock.org',
    install_requires=read_install_requires(),
    keywords='Global Financial Data',
    packages=find_packages(),
    include_package_data=True,
    package_data={'': ['*.csv', '*.txt']},
)