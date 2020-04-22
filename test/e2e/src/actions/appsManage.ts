import {Page, launch} from 'puppeteer';

export class appsManageAction{
    public async addApps(page:Page, appName:string, url:string, remark:string){
        
        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        await page.waitFor(1000);

        const appsManageBtn = await page.waitForSelector('a[href="#/admin/app"]');
        await appsManageBtn.click();

        await page.waitFor(2000);

        const addAppBtn = await page.waitForSelector('.ui-admin-apps-app-list--toolbar.flex-row .ivu-btn.ivu-btn-default');
        await addAppBtn.click();

        await page.waitFor(2000);

        const appNameInput = await page.waitForSelector('input[placeholder="填写应用名称"]');
        await appNameInput.type(appName);

        const urlInput = await page.waitForSelector('input[placeholder="填写主页地址"]');
        await urlInput.type(url);

        const remarkInput = await page.waitForSelector('input[placeholder="自定义备注"]');
        await remarkInput.type(remark);

        await page.waitFor(2000);

        const keepBtn = await page.waitForSelector('.buttons-right .ivu-btn.ivu-btn-primary');
        await keepBtn.click();

        await page.waitFor(3000);
    }

    public async editAppMassage(page:Page, appName:string, remark:string){
        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        await page.waitFor(2000);

        const appsManageBtn = await page.waitForSelector('a[href="#/admin/app"]');
        await appsManageBtn.click();
        
        const editAppBtn = await page.waitForSelector('.ivu-table-tbody>tr:first-child .flex-row span:nth-child(2)');
        await editAppBtn.click();

        await page.waitFor(2000);

        const appNameInput = await page.waitForSelector('input[placeholder="填写应用名称"]');
        await appNameInput.type(appName);

        const remarkInput = await page.waitForSelector('input[placeholder="自定义备注"]');
        await remarkInput.type(remark);

        await page.waitFor(1000);

        const keepBtn = await page.waitForSelector('.buttons-right .ivu-btn.ivu-btn-primary');
        await keepBtn.click();

        await page.waitFor(3000);

    }

    public async deleteApp(page:Page){
        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        const appsManageBtn = await page.waitForSelector('a[href="#/admin/app"]');
        await appsManageBtn.click();

        await page.waitFor(2000);
        
        const editAppBtn = await page.waitForSelector('.ivu-table-tbody>tr:first-child .flex-row span:nth-child(2)');
        await editAppBtn.click();

        await page.waitFor(2000);

        const deleteBtn = await page.waitForSelector('.ivu-btn.ivu-btn-error');
        await deleteBtn.click();

        await page.waitFor(2000);

    }

    public async userPower(page:Page, searchname:string){
        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        await page.waitFor(2000);

        const appsManageBtn = await page.waitForSelector('a[href="#/admin/app"]');
        await appsManageBtn.click();

        await page.waitFor(2000);

        const appBtn = await page.waitForSelector('.flex-row>span:nth-child(3)');
        await appBtn.click();

        await page.waitFor(2000);

        const editBtn = await page.waitForSelector('.permtags .table-btn');
        await editBtn.click();

        await page.waitFor(2000);

        const searchInput = await page.waitForSelector('input[placeholder="搜索账号"]');
        await searchInput.type(searchname);

        await page.waitFor(2000);

        const userCheckbox = await page.waitForSelector('div.ivu-cell-main > div.ivu-cell-title > label > span.ivu-checkbox > input');
        await userCheckbox.click();

        await page.waitFor(2000);

        const keepBtn = await page.waitForSelector('.ivu-btn.ivu-btn-primary.ivu-btn-large span');
        await keepBtn.click();

        await page.waitFor(400000);//等待权限生效

    }

    public async departmentPower(page:Page, searchname:string){
        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        await page.waitFor(2000);

        const appsManageBtn = await page.waitForSelector('a[href="#/admin/app"]');
        await appsManageBtn.click();

        await page.waitFor(2000);

        const appBtn = await page.waitForSelector('.flex-row>span:nth-child(3)');
        await appBtn.click();

        await page.waitFor(2000);

        const departmentPowerBtn = await page.waitForSelector('.ivu-menu.ivu-menu-light.ivu-menu-horizontal>li:nth-child(2)');
        await departmentPowerBtn.click();

        await page.waitFor(2000);

        const editBtn = await page.waitForSelector('.permtags .table-btn');
        await editBtn.click();

        await page.waitFor(2000);

        const searchInput = await page.waitForSelector('div.ui-choose-base--middle > div > div.search.ivu-input-wrapper.ivu-input-wrapper-default.ivu-input-type > input');
        await searchInput.type(searchname);

        await page.waitFor(1000);

        const departmentCheckbox = await page.waitForSelector('div.ui-choose-base--middle > div > ul > li:nth-child(1) > label > span.ivu-checkbox > input');
        await departmentCheckbox.click();

        await page.waitFor(2000);

        const keepBtn = await page.waitForSelector('div.ivu-modal-footer > div > div > button.ivu-btn.ivu-btn-primary');
        await keepBtn.click();

        await page.waitFor(400000);//等待权限生效

    }

}
