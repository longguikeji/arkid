import {Page, launch} from 'puppeteer';

export class personalSetAction{
    public async exit(page:Page){
        const settingBtn = await page.waitForSelector('.ivu-icon.ivu-icon-md-arrow-dropdown');
        await settingBtn.click();

        const exitBtn = await page.waitForSelector('.ivu-dropdown-menu>li');
        await exitBtn.click();
    }

    public async changePassword(page:Page, oldPwd:string, newPwd:string, renewPwd:string){
        const settingBtn = await page.waitForSelector('.ivu-icon.ivu-icon-md-arrow-dropdown');
        await settingBtn.click();

        const exitBtn = await page.waitForSelector('.ivu-dropdown-menu>li:last-child');
        await exitBtn.click();

        const oldPwdInput = await page.waitForSelector('input[placeholder="输入原密码"]');
        await oldPwdInput.type(oldPwd);

        const newPwdInput = await page.waitForSelector('input[placeholder="输入新密码"]');
        await oldPwdInput.type(newPwd);

        const renewPwdInput = await page.waitForSelector('input[placeholder="再次输入新密码"]');
        await oldPwdInput.type(renewPwd);

        const defineBtn = await page.waitForSelector('.right-button.ivu-btn.ivu-btn-primary');
        await defineBtn.click();
        
    }

}