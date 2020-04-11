import {Page, launch} from 'puppeteer';

export class accountAction{
    public async addAccount(page:Page, username:string, name:string, password:string, 
        repassword:string, phone:string, personalemail:string, email:string){

        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        await page.waitFor(2000);

        const addAccountBtn = await page.waitForSelector('.ivu-btn.ivu-btn-primary');
        await addAccountBtn.click();

        const usernameInput = await page.waitForSelector('input[placeholder="请输入 用户名"]');
        await usernameInput.type(username);

        const nameInput = await page.waitForSelector('input[placeholder="请输入 姓名"]');
        await nameInput.type(name);

        const pwdBtn = await page.waitForSelector('.ivu-form-item-content .ivu-btn.ivu-btn-primary');
        await pwdBtn.click();

        await page.waitFor(2000);

        const pwdInput = await page.waitForSelector('input[placeholder="请添加新登录密码"]');
        await pwdInput.type(password);

        const repwdInput = await page.waitForSelector('input[placeholder="再次输入登录密码"]');
        await repwdInput.type(repassword);

        await page.waitFor(2000);

        const primaryBtn= await page.waitForSelector('div.ivu-modal-footer > div > button.ivu-btn.ivu-btn-primary');
        await primaryBtn.click();

        await page.waitFor(1000);

        const phoneInput = await page.waitForSelector('input[placeholder="请输入 手机"]');
        await phoneInput.type(phone);

        const perEmailInput = await page.waitForSelector('.form.ivu-form.ivu-form-label-right>div:nth-child(5) .ivu-input.ivu-input-default');
        await perEmailInput.type(personalemail);

        const emailInput = await page.waitForSelector('.form.ivu-form.ivu-form-label-right>div:nth-child(6) .ivu-input.ivu-input-default');
        await emailInput.type(email);

        const addBtn = await page.waitForSelector('.drawer-footer.flex-row.flex-auto .ivu-btn.ivu-btn-primary');
        await addBtn.click();

    }

    public async setAccount(page:Page, did:string, dsecret:string, meskey:string, messecret:string, mesform:string, mesluok:string){

        const setActBtn = await page.waitForSelector('a[href="#/admin/account/settings"]');
        await setActBtn.click();

        const closeBtn = await page.waitForSelector('.ivu-radio .ivu-radio-input');
        await closeBtn.click();

        const openBtn = await page.waitForSelector('.ivu-radio.ivu-radio-checked .ivu-radio-input');
        await openBtn.click();

        const dSetBtn = await page.waitForSelector('.ivu-checkbox .ivu-checkbox-input');
        await dSetBtn.click();

        const dSet = await page.waitForSelector('.thirdparty-login .content>div:first-child .link');
        await dSet.click();

        const dIdInput = await page.waitForSelector('input[placeholder="填写 App Id"]');
        await dIdInput.type(did);

        const dSecretInput = await page.waitForSelector('input[placeholder="填写 App Secret"]');
        await dSecretInput.type(dsecret);

        const keepBtn = await page.waitForSelector('.footer>button:last-child');
        await keepBtn.click();

        const phoneLogonBtn = await page.waitForSelector('.ivu-checkbox.ivu-checkbox-checked .ivu-checkbox-input');
        await phoneLogonBtn.click();

        const messageSet = await page.waitForSelector('.register-type .content>div:last-child .link');
        await messageSet.click();
        
        const mesKeyInput = await page.waitForSelector('input[placeholder="填写 Access Key"]');
        await mesKeyInput.type(meskey);

        const mesSecretInput = await page.waitForSelector('input[placeholder="填写 Access Secret"]');
        await mesSecretInput.type(messecret);

        const mesFormInput = await page.waitForSelector('input[placeholder="填写短信模板"]');
        await mesFormInput.type(mesform);

        const mesLuokInput = await page.waitForSelector('input[placeholder="填写短信落款"]');
        await mesLuokInput.type(mesluok);

        const mesKeepBtn = await page.waitForSelector('.footer>button:last-child');
        await mesKeepBtn.click();

        const keepReviseBtn = await page.waitForSelector('.register-submit .ivu-btn.ivu-btn-default');
        await keepReviseBtn.click();

        const goDisposeBtn = await page.waitForSelector('a[href="#/admin/config"]');
        await goDisposeBtn.click();

        const accountBtn = await page.waitForSelector('a[href="#/admin/account"]');
        await accountBtn.click();

    }

    public async synchroAccount(page:Page, dkey:string, dsecret:string, dcorpid:string, dcorpsecret:string){

        const synchroAcBtn = await page.waitForSelector('a[href="#/admin/account/thirdparty"]');
        await synchroAcBtn.click();

        const dAccountBtn = await page.waitForSelector('.third-party-list .name');
        await dAccountBtn.click();

        const dKeyInput = await page.waitForSelector('.form.ivu-form.ivu-form-label-right>div:first-child .ivu-input.ivu-input-default');
        await dKeyInput.type(dkey);

        const dSecretInput = await page.waitForSelector('.form.ivu-form.ivu-form-label-right>div:nth-child(2) .ivu-input.ivu-input-default');
        await dSecretInput.type(dsecret);

        const dCorpIdInput = await page.waitForSelector('.form.ivu-form.ivu-form-label-right>div:nth-child(3) .ivu-input.ivu-input-default');
        await dCorpIdInput.type(dcorpid);

        const dCorpSecret = await page.waitForSelector('.form.ivu-form.ivu-form-label-right>div:last-child .ivu-input.ivu-input-default');
        await dCorpSecret.type(dcorpsecret);

        const keepSetBtn = await page.waitForSelector('.btns>button:first-child');
        await keepSetBtn.click();

        const synchroBtn = await page.waitForSelector('.btns>button:last-child');
        await synchroBtn.click();
    }

    public async searchAccount(page:Page, search:string){

        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        const searchAccountInput = await page.waitForSelector('.ivu-input.ivu-input-default.ivu-input-with-suffix');
        await searchAccountInput.type(search);

        await page.waitFor(4000);

    }

    public async reviseAccount(page:Page, name:string, password:string, repassword:string){

        const reviseAccount = await page.waitForSelector('.ivu-table-cell>div>span:first-child');
        await reviseAccount.click();

        const nameInput = await page.waitForSelector('input[placeholder="请输入 姓名"]');
        
        await nameInput.type(name);

        const pwdBtn = await page.waitForSelector('.ivu-form-item-content .ivu-btn.ivu-btn-primary');
        await pwdBtn.click();

        const pwdInput = await page.waitForSelector('input[placeholder="请添加新登录密码"]');
        await pwdInput.type(password);

        const repwdInput = await page.waitForSelector('input[placeholder="再次输入登录密码"]');
        await repwdInput.type(repassword);

        await page.waitFor(2000);

        const primaryBtn= await page.waitForSelector('div.ivu-modal-footer > div > button.ivu-btn.ivu-btn-primary');
        await primaryBtn.click();

        await page.waitFor(2000);

        const addBtn = await page.waitForSelector('div.drawer-footer.flex-row.flex-auto > button.ivu-btn.ivu-btn-primary');
        await addBtn.click();

        await page.waitFor(3000);

    }

    public async deleteAccount(page:Page){

        const checkbox = await page.waitForSelector('.ivu-table-body.ivu-table-overflowX > table > tbody > tr > td.ivu-table-column-center > div > label > span > input');
        await checkbox.click();

        const deleteAccountBtn = await page.waitForSelector('.ui-account-page .flex-row.flex-auto>button:last-child');
        await deleteAccountBtn.click();

        const deleteBtn = await page.waitForSelector('.ivu-modal-confirm-footer>button:last-child');
        await deleteBtn.click();

        await page.waitFor(2000);

    }
}