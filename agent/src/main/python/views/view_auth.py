#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-04-08 16:40:20
# @Desc    : 授权配置
# @File    : view_auth.py
from flask import redirect, render_template, flash, Blueprint, request, url_for
from flask_login import login_user, current_user, logout_user

from application_config import db, app
from application_config import login_manager
from bin.assets import compile_auth_assets
from db.models import User
from form.form_auth import AuthSignin, AuthSignup

from services.service_user import UserService

auth_view = Blueprint('auth_view', __name__, template_folder='templates', static_folder='static')

compile_auth_assets(app)


@auth_view.route('/signin', methods=['GET', 'POST'])
def signin():
    """
    登录视图
    """
    if current_user.is_authenticated:
        return redirect(url_for('host_view.list'))
    login_form = AuthSignin()
    if request.method == 'POST':
        if login_form.validate_on_submit():
            email = login_form.email.data
            password = login_form.password.data
            user = UserService().find_by_email(email=email)
            if user and user.check_password(password=password):
                login_user(user)
                next_page = request.args.get('next')
                return redirect(next_page or url_for('host_view.list'))
        flash('无效的账号/密码')
        return redirect(url_for('auth_view.signin'))
    return render_template('auth/signin.html', form=login_form, title='用户登录')

@auth_view.route('/sign_out')
def logout():
    logout_user()
    flash(u'当前用户已经退出登录')
    return redirect(url_for('auth_view.signin'))

@auth_view.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    用户注册
    GET: 注册页面
    POST: 如果提交的凭证有效，将用户重定向到登录的主页
    """
    signup_form = AuthSignup()
    if request.method == 'POST':
        print signup_form.validate_on_submit()
        if signup_form.validate_on_submit():
            name = signup_form.name.data
            email = signup_form.email.data
            password = signup_form.password.data
            confirm_password = signup_form.confirm_password.data
            existing_user = UserService().find_by_email(email=email)
            if existing_user is None:
                user = User(name=name, email=email, password=password)
                if UserService().add(user=user):
                    login_user(user)
                    return redirect(url_for('host_view.list'), code=400)
            flash('该电子邮件地址已经被注册')
            return redirect(url_for('auth_view.signup'))
    return render_template('auth/signup.html', title='注册账号', form=signup_form)


@login_manager.user_loader
def load_user(user_id):
    """
    检查用户是否登录
    :param user_id: 用户ID
    :return: 登录状态
    """
    if user_id is not None:
        return User.query.get(user_id)
    return None


@login_manager.unauthorized_handler
def unauthorized():
    """
    将未经授权的用户重定向到503界面
    :return: 重定向
    """
    flash('您没有权限访问当前页面，请登录。')
    return redirect(url_for('auth_view.signin'))
