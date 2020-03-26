import {Page, launch} from 'puppeteer';

export class managerSettingAction{
    public async managerSetting(page:Page, search:string){//特定账号和分组未分配权限
        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        const managerBtn = await page.waitForSelector('a[href="href="#/admin/manager"]');
        await managerBtn.click();

        const addManagerBtn = await page.waitForSelector('.ui-manager-page--header .ivu-btn.ivu-btn-default');
        await addManagerBtn.click();

        const selectUserBtn = await page.waitForSelector('span.placeholder');
        await selectUserBtn.click();

        const userCheckbox = await page.waitForSelector('.user-list>li .ivu-checkbox-input');
        await userCheckbox.click();

        const keepBtn = await page.waitForSelector('.ui-choose-base--footer.flex-row .ivu-btn.ivu-btn-primary');
        await keepBtn.click();

        const manageScopeBtn = await page.waitForSelector('div[name="ivuRadioGroup_1585204233336_1"]>label:last-child input[name="ivuRadioGroup_1585204233336_1"]');
        await manageScopeBtn.click();

        const scopeBtn = await page.waitForSelector('.manager-settings-scopes .placeholder');
        await scopeBtn.click();

        const groupBtn = await page.waitForSelector('.base-list>li:nth-child(2)');
        await groupBtn.click();

        const searchUserInput = await page.waitForSelector('input[placeholder="搜索"]');
        await searchUserInput.type(search);

        const selectCheckbox = await page.waitForSelector('.ui-choose-base--middle .ivu-checkbox-input');
        await selectCheckbox.click();

        const keepScopeBtn = await page.waitForSelector('.ivu-modal-footer .ui-choose-base--footer.flex-row .ivu-btn.ivu-btn-primary');
        await keepScopeBtn.click();

        const addBtn = await page.waitForSelector('.ui-edit-manager-page--footer .ivu-btn.ivu-btn-primary');
        await addBtn.click();

    } 
}