import {Page, launch} from 'puppeteer';

export class configManageAction{
    
    public async loginSetting(page:Page, companyname:string){
       // const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        //await manageBtn.click();

        const configManageBtn = await page.waitForSelector('a[href="#/admin/config"]');
        await configManageBtn.click();

        const companyNameInput = await page.waitForSelector('input[placeholder="请输入公司名称"]');
        await companyNameInput.type(companyname);

        const colorBtn = await page.waitForSelector('.ivu-select-selection');
        await colorBtn.click();

        const selectColor = await page.waitForSelector('.ivu-select-dropdown-list>li:nth-child(2)');
        await selectColor.click();

        await page.waitFor(2000);

        const keepBtn = await page.waitForSelector('div.ui-admin-config-save.flex-row > div > button > span');
        await keepBtn.click();

        await page.waitFor(3000);

    }

    public async urlTest(page:Page){
       // const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
       // await manageBtn.click();

        await page.waitFor(1000);

        const configManageBtn = await page.waitForSelector('a[href="#/admin/config"]');
        await configManageBtn.click();

        await page.waitFor(2000);
        
        const urlBtn = await page.waitForSelector('.go-to-accountconfig');
        await urlBtn.click();

        await page.waitFor(2000);
    }

}
