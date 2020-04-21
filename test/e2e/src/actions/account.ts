import {Page, launch} from 'puppeteer';

export class accountAction{
    public async addAccount(page:Page, username:string, name:string, password:string, 
        repassword:string, phone:string, personalemail:string, email:string){
        
        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();
        
        console.log(page.url());
        await page.waitFor(5000);

        const addAccountBtn = await page.waitForSelector('div.ui-user-list-toolbar.flex-row > div.flex-row.flex-auto > button.ivu-btn.ivu-btn-primary');
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

    public async searchAccount(page:Page, search:string){

        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        await page.waitFor(2000);

        const searchAccountInput = await page.waitForSelector('.ivu-input.ivu-input-default.ivu-input-with-suffix');
        await searchAccountInput.type(search);

        await page.waitFor(4000);

    }

    public async reviseAccount(page:Page, name:string, password:string, repassword:string){

        const reviseAccount = await page.waitForSelector('.ivu-table-cell>div>span:first-child');
        await reviseAccount.click();
 
        await page.waitFor(3000);

        const nameInput = await page.waitForSelector('input[placeholder="请输入 姓名"]');
        await nameInput.type(name);

        const pwdBtn = await page.waitForSelector('.ivu-form-item-content .ivu-btn.ivu-btn-primary');
        await pwdBtn.click();
        
        await page.waitFor(2000);

        const pwdInput = await page.waitForSelector('input[placeholder="请添加新登录密码"]');
        await pwdInput.type(password);

        await page.waitFor(2000);

        const repwdInput = await page.waitForSelector('input[placeholder="再次输入登录密码"]');
        await repwdInput.type(repassword);

        await page.waitFor(5000);

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
