#!/usr/bin/env python3
# -*- coding: utf-8 -*-



import requests

#POSTメソッド(url:urlを指定(str)、header:認証コード（アクセストークンとアクセストークンシークレット）を指定(bytes)、param:parameterを指定(json))
def post(url, basic_user_and_pasword, body):
    response=requests.post(url,headers={"Authorization": "Basic " + basic_user_and_pasword.decode('utf-8')},json=body)
    return response.json()

#GETメソッド(url:urlを指定(str)、header:認証コード（アクセストークンとアクセストークンシークレット）を指定(bytes)、param:parameterを指定(json))
def get(url, basic_user_and_pasword, payload={}):
    response=requests.get(url,headers={"Authorization": "Basic " + basic_user_and_pasword.decode('utf-8')},json=payload)
    return response.json()

#PUTメソッド(url:urlを指定(str)、header:認証コード（アクセストークンとアクセストークンシークレット）を指定(bytes)、param:parameterを指定(json))
def put(url, basic_user_and_pasword, payload={}):
    response=requests.put(url,headers={"Authorization": "Basic " + basic_user_and_pasword.decode('utf-8')},json=payload)
    return response.json()

#DELETEメソッド(url:urlを指定(str)、header:認証コード（アクセストークンとアクセストークンシークレット）を指定(bytes)、param:parameterを指定(json))
def delete(url, basic_user_and_pasword, payload={}):
    response=requests.delete(url,headers={"Authorization": "Basic " + basic_user_and_pasword.decode('utf-8')},json=payload)
    return response.json()






















