import {Page, launch} from 'puppeteer';

export class configManageAction{
    public async loginSetting(page:Page, companyname:string){
        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        const configManageBtn = await page.waitForSelector('a[href="#/admin/app"]');
        await configManageBtn.click();

        const companyNameInput = await page.waitForSelector('input[placeholder="请输入公司名称"]');
        await companyNameInput.type(companyname);

        const colorBtn = await page.waitForSelector('.ivu-select-selection');
        await colorBtn.click();

        const selectColor = await page.waitForSelector('.ivu-select-dropdown-list>li:nth-child(2)');
        await selectColor.click();

        const keepBtn = await page.waitForSelector('.admin-save-button.ivu-btn.ivu-btn-primary span');
        await keepBtn.click();

    }

    public async urlTest(page:Page){
        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        const configManageBtn = await page.waitForSelector('a[href="#/admin/app"]');
        await configManageBtn.click();
        
        const urlBtn = await page.waitForSelector('.go-to-accountconfig');
        await urlBtn.click();
    }

}