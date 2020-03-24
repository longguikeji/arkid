import {Page, launch} from 'puppeteer';

export class appsManageAction{
    public async addApps(page:Page, appName:string, url:string, remark:string){
        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        const appsManageBtn = await page.waitForSelector('a[href="href="#/admin/app"]');
        await appsManageBtn.click();

        const addAppBtn = await page.waitForSelector('.ui-admin-apps-app-list--toolbar.flex-row .ivu-btn.ivu-btn-default');
        await addAppBtn.click();

        const appNameInput = await page.waitForSelector('input[placeholder="填写应用名称]');
        await appNameInput.type(appName);

        const urlInput = await page.waitForSelector('input[placeholder="填写主页地址]');
        await urlInput.type(url);

        const remarkInput = await page.waitForSelector('input[placeholder="自定义备注"]');
        await remarkInput.type(remark);

        const keepBtn = await page.waitForSelector('.buttons-right .ivu-btn.ivu-btn-primary');
        await keepBtn.click();
    }

    public async editAppMassage(page:Page, appName:string, remark:string){
        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        const appsManageBtn = await page.waitForSelector('a[href="href="#/admin/app"]');
        await appsManageBtn.click();
        
        const editAppBtn = await page.waitForSelector('.ivu-table-tbody>tr:last-child .flex-row span:nth-child(2)');
        await editAppBtn.click();

        const appNameInput = await page.waitForSelector('input[placeholder="填写应用名称]');
        await appNameInput.type(appName);

        const remarkInput = await page.waitForSelector('input[placeholder="自定义备注"]');
        await remarkInput.type(remark);

        const keepBtn = await page.waitForSelector('.buttons-right .ivu-btn.ivu-btn-primary');
        await keepBtn.click();

    }

    public async deleteApp(page:Page){
        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        const appsManageBtn = await page.waitForSelector('a[href="href="#/admin/app"]');
        await appsManageBtn.click();
        
        const editAppBtn = await page.waitForSelector('.ivu-table-tbody>tr:last-child .flex-row span:nth-child(2)');
        await editAppBtn.click();

        const deleteBtn = await page.waitForSelector('.ivu-btn.ivu-btn-error');
        await deleteBtn.click();

    }
}