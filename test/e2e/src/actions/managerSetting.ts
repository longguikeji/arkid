import {Page, launch} from 'puppeteer';

export class managerSettingAction{
    public async managerSetting(page:Page){//所在分组及下级分组未分配权限

        const addManagerBtn = await page.waitForSelector('.ui-manager-page--header .ivu-btn.ivu-btn-default');
        await addManagerBtn.click();

        await page.waitFor(2000);

        const selectUserBtn = await page.waitForSelector('span.placeholder');
        await selectUserBtn.click();

        await page.waitFor(2000);

        const userCheckbox = await page.waitForSelector('.user-list>li .ivu-checkbox-input');
        await userCheckbox.click();

        await page.waitFor(2000);

        const keepBtn = await page.waitForSelector('.ui-choose-base--footer.flex-row .ivu-btn.ivu-btn-primary');
        await keepBtn.click();

        await page.waitFor(3000);

        const addBtn = await page.waitForSelector('.ui-edit-manager-page--footer .ivu-btn.ivu-btn-primary');
        await addBtn.click();

        await page.waitFor(2000);

    } 

    public async managerSettinga(page:Page, search:string){//特定分组分配创建大类权限
        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        await page.waitFor(2000);

        const managerBtn = await page.waitForSelector('a[href="#/admin/manager"]');
        await managerBtn.click();

        await page.waitFor(3000);

        const addManagerBtn = await page.waitForSelector('.ui-manager-page--header .ivu-btn.ivu-btn-default');
        await addManagerBtn.click();

        await page.waitFor(2000);

        const selectUserBtn = await page.waitForSelector('span.placeholder');
        await selectUserBtn.click();

        await page.waitFor(2000);

        const userCheckbox = await page.waitForSelector('.user-list>li:nth-child(2) .ivu-checkbox-input');
        await userCheckbox.click();

        await page.waitFor(2000);

        const keepBtn = await page.waitForSelector('.ui-choose-base--footer.flex-row .ivu-btn.ivu-btn-primary');
        await keepBtn.click();

        await page.waitFor(2000);

        const manageScopeBtn = await page.waitForSelector('div.manager-settings-scopes > div > div > label:nth-child(2) > span > input');
        await manageScopeBtn.click();

        await page.waitFor(2000);

        const scopeBtn = await page.waitForSelector('.manager-settings-scopes .placeholder');
        await scopeBtn.click();

        await page.waitFor(2000);

        const groupBtn = await page.waitForSelector('.base-list>li:nth-child(2)');
        await groupBtn.click();

        const searchUserInput = await page.waitForSelector('input[placeholder="搜索"]');
        await searchUserInput.type(search);

        await page.waitFor(2000);

        const selectCheckbox = await page.waitForSelector('.ui-choose-base--middle .ivu-checkbox-input');
        await selectCheckbox.click();

        const keepScopeBtn = await page.waitForSelector('.ivu-modal-footer .ui-choose-base--footer.flex-row .ivu-btn.ivu-btn-primary');
        await keepScopeBtn.click();

        await page.waitFor(2000);

        const creatGroupBtn = await page.waitForSelector('.ivu-checkbox-group.ivu-checkbox-default>ul>li .ivu-checkbox-input');
        await creatGroupBtn.click();

        const addBtn = await page.waitForSelector('.ui-edit-manager-page--footer .ivu-btn.ivu-btn-primary');
        await addBtn.click();

        await page.waitFor(2000);

    } 

    public async managerSettingb(page:Page, searchName:string){//所在分组及下级分组分配创建应用和查看日志权限
        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        const managerBtn = await page.waitForSelector('a[href="href="#/admin/manager"]');
        await managerBtn.click();

        const addManagerBtn = await page.waitForSelector('.ui-manager-page--header .ivu-btn.ivu-btn-default');
        await addManagerBtn.click();

        const selectUserBtn = await page.waitForSelector('span.placeholder');
        await selectUserBtn.click();

        const searchUserInput = await page.waitForSelector('input[placeholder="搜索"]');
        await searchUserInput.type(searchName);

        const userCheckbox = await page.waitForSelector('.user-list>li .ivu-checkbox-input');
        await userCheckbox.click();

        const keepBtn = await page.waitForSelector('.ui-choose-base--footer.flex-row .ivu-btn.ivu-btn-primary');
        await keepBtn.click();

        const creatAppBtn = await page.waitForSelector('.ivu-checkbox-group.ivu-checkbox-default>ul>li:nth-child(2) .ivu-checkbox-input');
        await creatAppBtn.click();

        const lookLogBtn = await page.waitForSelector('.ivu-checkbox-group.ivu-checkbox-default>ul>li:nth-child(3) .ivu-checkbox-input');
        await lookLogBtn.click();

        const addBtn = await page.waitForSelector('.ui-edit-manager-page--footer .ivu-btn.ivu-btn-primary');
        await addBtn.click();

    }

    public async managerSettingc(page:Page, searchName:string){//所在分组及下级分组公司基础信息配置
        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        const managerBtn = await page.waitForSelector('a[href="href="#/admin/manager"]');
        await managerBtn.click();

        const addManagerBtn = await page.waitForSelector('.ui-manager-page--header .ivu-btn.ivu-btn-default');
        await addManagerBtn.click();

        const selectUserBtn = await page.waitForSelector('span.placeholder');
        await selectUserBtn.click();

        const searchUserInput = await page.waitForSelector('input[placeholder="搜索"]');
        await searchUserInput.type(searchName);

        const userCheckbox = await page.waitForSelector('.user-list>li .ivu-checkbox-input');
        await userCheckbox.click();

        const keepBtn = await page.waitForSelector('.ui-choose-base--footer.flex-row .ivu-btn.ivu-btn-primary');
        await keepBtn.click();

        const companySetBtn = await page.waitForSelector('.ivu-checkbox-group.ivu-checkbox-default>ul>li:nth-child(4) .ivu-checkbox-input');
        await companySetBtn.click();

        const addBtn = await page.waitForSelector('.ui-edit-manager-page--footer .ivu-btn.ivu-btn-primary');
        await addBtn.click();

    }

    public async managerSettingd(page:Page, searchName:string){//所在分组及下级分组应用111权限
        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        const managerBtn = await page.waitForSelector('a[href="href="#/admin/manager"]');
        await managerBtn.click();

        const addManagerBtn = await page.waitForSelector('.ui-manager-page--header .ivu-btn.ivu-btn-default');
        await addManagerBtn.click();

        const selectUserBtn = await page.waitForSelector('span.placeholder');
        await selectUserBtn.click();

        const searchUserInput = await page.waitForSelector('input[placeholder="搜索"]');
        await searchUserInput.type(searchName);

        const userCheckbox = await page.waitForSelector('.user-list>li .ivu-checkbox-input');
        await userCheckbox.click();

        const keepBtn = await page.waitForSelector('.ui-choose-base--footer.flex-row .ivu-btn.ivu-btn-primary');
        await keepBtn.click();

        const appCheckbox = await page.waitForSelector('.perm-settings-main-app-list>div>ul>li .ivu-checkbox');
        await appCheckbox.click();

        const addBtn = await page.waitForSelector('.ui-edit-manager-page--footer .ivu-btn.ivu-btn-primary');
        await addBtn.click();

    }

    public async editManager(page:Page){//编辑管理员222222的权限
        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        const managerBtn = await page.waitForSelector('a[href="href="#/admin/manager"]');
        await managerBtn.click();

        const editManagerBtn = await page.waitForSelector('.ivu-table-tbody>tr:last-child>td:last-child a');
        await editManagerBtn.click();

        const logCheckbox = await page.waitForSelector('.ivu-checkbox-group.ivu-checkbox-default>ul>li:nth-child(3) .ivu-checkbox');
        await logCheckbox.click();

        const addBtn = await page.waitForSelector('.ui-edit-manager-page--footer .ivu-btn.ivu-btn-primary');
        await addBtn.click();

    }

    public async deleteManager(page:Page){//删除管理员222222
        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        const managerBtn = await page.waitForSelector('a[href="href="#/admin/manager"]');
        await managerBtn.click();

        const editManagerBtn = await page.waitForSelector('.ivu-table-tbody>tr:last-child>td:last-child a');
        await editManagerBtn.click();

        const logCheckbox = await page.waitForSelector('.ivu-checkbox-group.ivu-checkbox-default>ul>li:nth-child(3) .ivu-checkbox');
        await logCheckbox.click();

        const deleteBtn = await page.waitForSelector('.ui-edit-manager-page--footer-wrapper .ivu-btn.ivu-btn-error');
        await deleteBtn.click();

        const keepBtn = await page.waitForSelector('.ivu-btn.ivu-btn-primary.ivu-btn-large');
        await keepBtn.click();

    }

}