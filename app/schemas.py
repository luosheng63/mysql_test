# schemas.py
from marshmallow import Schema, fields, validates_schema, ValidationError, post_load
import re

class BasePhoneSchema(Schema):
    phone = fields.Str(required=True, error_messages={"required": "手机号不能为空"})

    @validates_schema
    def validate_phone(self, data, **kwargs):
        phone = data.get('phone')
        
        if phone is None:
            raise ValidationError("手机号不能为空", "phone")
        
        # 确保是字符串
        if not isinstance(phone, str):
            phone = str(phone)
        
        # 去除空格
        phone = phone.strip()
        
        if not re.match(r'^1[3-9]\d{9}$', phone):
            raise ValidationError("手机号格式不正确", "phone")
        
        # 更新数据中的 phone（确保是干净的字符串）
        data['phone'] = phone
        return data

class SendCodeSchema(BasePhoneSchema):
    pass

class RegisterSchema(BasePhoneSchema):
    code = fields.Str(required=True, error_messages={"required": "验证码不能为空"})
    password = fields.Str(required=True, error_messages={"required": "密码不能为空"})

    @validates_schema
    def validate_password(self, data, **kwargs):
        password = data.get('password')
        
        if password is None:
            raise ValidationError("密码不能为空", "password")
        
        if len(password) < 8 or len(password) > 20:
            raise ValidationError("密码长度需在8-20位之间", "password")
        
        if not re.search(r'[A-Za-z]', password) or not re.search(r'\d', password):
            raise ValidationError("密码必须包含字母和数字", "password")
        
        return data

class LoginSchema(BasePhoneSchema):
    password = fields.Str(required=True, error_messages={"required": "密码不能为空"})

# 用于 Profile 更新的 Schema
class UpdateProfileSchema(Schema):
    nickname = fields.Str(allow_none=True, validate=lambda x: len(x) <= 12 if x else True)
    gender = fields.Int(allow_none=True, validate=lambda x: x in [0, 1, 2])
    birthday = fields.Date(allow_none=True)