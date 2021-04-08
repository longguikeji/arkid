class ButtonRedirect(dict):
    def __init__(self, url:str, params:dict=None, *args, **kwargs):
        self['url'] = url
        if params:
            self['params'] = params
        super().__init__(*args, **kwargs)


class ButtonHttp(dict):
    def __init__(self, url:str, method:str, params:dict=None, *args, **kwargs):
        self['url'] = url
        self['method'] = method
        if params:
            self['params'] = params
        super().__init__(*args, **kwargs)

class Button(dict):
    def __init__(self, prepend:str=None, label:str=None, tooltip:str=None, long:bool=False, img:str=None, gopage:str=None, redirect:ButtonRedirect=None, http:ButtonHttp=None, delay:int=None, *args, **kwargs):
        if prepend:
            self['prepend'] = prepend
        if label:
            self['label'] = label
        if tooltip:
            self['tooltip'] = tooltip
        if long:
            self['long'] = long
        if img:
            self['img'] = img
        if gopage:
            self['gopage'] = gopage
        if redirect:
            self['redirect'] = redirect
        if http:
            self['http'] = http
        if delay:
            self['delay'] = delay
        super().__init__(*args, **kwargs)

class LoginFormItem(dict):
    def __init__(self, type:str, name:str, placeholder:str=None, append:Button=None, *args, **kwargs):
        self['type'] = type
        self['name'] = name
        if placeholder:
            self['placeholder'] = placeholder
        if append:
            self['append'] = append
        super().__init__(*args, **kwargs)

class LoginForm(dict):
    def __init__(self, label:str, items:[LoginFormItem], submit:Button, *args, **kwargs):
        self['label'] = label
        self['items'] = items
        self['submit'] = submit
        super().__init__(*args, **kwargs)

class LoginPageExtend(dict):
    def __init__(self, title:str=None, buttons:[Button]=None, *args, **kwargs):
        if title:
            self['title'] = title
        if buttons:
            self['buttons'] = buttons
        super().__init__(*args, **kwargs)

    def merge(self, extend):
        if extend.get('title',None):
            self['title'] = extend.get('title')
        self.addButtons(extend.get('buttons'))

    def addButtons(self, buttons):
        if buttons:
            _buttons = self.get('buttons',[])
            _buttons.extend(buttons)
            self['buttons'] = _buttons

class LoginPage(dict):
    def __init__(self, name:str, forms:[LoginForm]=None, bottoms:[Button]=None, extend:LoginPageExtend=None, *args, **kwargs):
        self['name'] = name
        if forms:
            self['forms'] = forms
        if bottoms:
            self['bottoms'] = bottoms
        if extend:
            self['extend'] = extend
        super().__init__(*args, **kwargs)
    
    def merge(self, page):
        if page.get('forms',None):
            self.addForms(page.get('forms'))
        if page.get('bottoms',None):
            self.addBottoms(page.get('bottoms'))
        if page.get('extend',None):
            self.addExtend(page.get('extend'))

    def addForms(self, forms:[LoginForm]):
        if forms:
            _forms = self.get('forms',[])
            _forms.extend(forms)
            self['forms'] = _forms

    def addBottoms(self, bottoms:[Button]):
        if bottoms:
            _bottoms = self.get('bottoms',[])
            _bottoms.extend(bottoms)
            self['bottoms'] = _bottoms

    def addExtend(self, extend:LoginPageExtend):
        if extend:
            _extend = self.get('extend',None)
            if _extend is not None:
                _extend.merge(extend)
            else:
                self['extend'] = extend

class LoginPages(dict):

    def __init__(self, *args, **kwargs):
        self['data'] = {}
        super().__init__(*args, **kwargs)

    def setTenant(self, tenant):
        if tenant:
            self['tenant'] = tenant

    def addPage(self, page:LoginPage):
        page_hash = self.get('data')
        _page:LoginPage = page_hash.get(page['name'], None)
        if _page is None:
            page_hash[page.get('name')] = page
        else:
            _page.merge(page)

    def addForm(self, page, form:LoginForm):
        if form:
            self.addPage(LoginPage(
                name=page,
                forms=[form]
            ))

    def addBottom(self, page, bottom:Button):
        if bottom:
            self.addPage(LoginPage(
                name=page,
                bottoms=[bottom]
            ))

    def addExtend(self, page, extend:LoginPageExtend):
        if extend:
            self.addPage(LoginPage(
                name=page,
                extend=extend
            ))

    def addExtendButton(self, page, button:Button):
        if button:
            self.addExtend(page, LoginPageExtend(
                buttons=[button]
            ))

    def setExtendTitle(self, page, title):
        if title:
            self.addExtend(page, LoginPageExtend(
                title=title
            ))

    def getPage(self, page):
        return self.get('data').get(page,None)


LOGIN = 'login'
REGISTER = 'register'
PASSWORD = 'password'
BIND = 'bind'