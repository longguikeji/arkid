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

        await page.waitFor(200000);

    } 

    public async managerSettinga(page:Page, search:string){//特定分组分配创建用户权限
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

        await page.waitFor(3000);

        const searchUserInput = await page.waitForSelector('div.search.ivu-input-wrapper.ivu-input-wrapper-default.ivu-input-type > input');
        await searchUserInput.type(search);

        await page.waitFor(2000);

        const selectCheckbox = await page.waitForSelector('body > div:nth-child(7) > div.ivu-modal-wrap.ui-choose-base > div > div > div.ivu-modal-body > div > div.ui-choose-base--middle > div > ul > li > label > span.ivu-checkbox > input');
        await selectCheckbox.click();

        const keepScopeBtn = await page.waitForSelector('body > div:nth-child(7) > div.ivu-modal-wrap.ui-choose-base > div > div > div.ivu-modal-footer > div > div > button.ivu-btn.ivu-btn-primary');
        await keepScopeBtn.click();

        await page.waitFor(2000);

        const creatUserBtn = await page.waitForSelector('.ivu-checkbox-group.ivu-checkbox-default>ul>li .ivu-checkbox-input');
        await creatUserBtn.click();

        const addBtn = await page.waitForSelector('.ui-edit-manager-page--footer .ivu-btn.ivu-btn-primary');
        await addBtn.click();

        await page.waitFor(300000);

    } 

    public async managerSettingb(page:Page, search:string){//特定账号和分组分配创建应用和查看日志权限
        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        await page.waitFor(1000);

        const managerBtn = await page.waitForSelector('a[href="#/admin/manager"]');
        await managerBtn.click();

        await page.waitFor(5000);

        const addManagerBtn = await page.waitForSelector('.ui-manager-page--header .ivu-btn.ivu-btn-default');
        await addManagerBtn.click();

        await page.waitFor(2000);

        const selectUserBtn = await page.waitForSelector('span.placeholder');
        await selectUserBtn.click();

        await page.waitFor(2000);

        const userCheckbox = await page.waitForSelector('.user-list>li:nth-child(3) .ivu-checkbox-input');
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

        const groupBtn = await page.waitForSelector('.base-list>li:nth-child(3)');
        await groupBtn.click();

        await page.waitFor(3000);

        const searchUserInput = await page.waitForSelector('div.search.ivu-input-wrapper.ivu-input-wrapper-default.ivu-input-type > input');
        await searchUserInput.type(search);

        await page.waitFor(2000);

        const selectCheckbox = await page.waitForSelector('body > div:nth-child(7) > div.ivu-modal-wrap.ui-choose-base > div > div > div.ivu-modal-body > div > div.ui-choose-base--middle > div > ul > li > label > span.ivu-checkbox > input');
        await selectCheckbox.click();

        const keepScopeBtn = await page.waitForSelector('body > div:nth-child(7) > div.ivu-modal-wrap.ui-choose-base > div > div > div.ivu-modal-footer > div > div > button.ivu-btn.ivu-btn-primary');
        await keepScopeBtn.click();

        await page.waitFor(2000);

        const creatAppBtn = await page.waitForSelector('.ivu-checkbox-group.ivu-checkbox-default>ul>li:nth-child(3) .ivu-checkbox-input');
        await creatAppBtn.click();

        const lookLogBtn = await page.waitForSelector('.ivu-checkbox-group.ivu-checkbox-default>ul>li:nth-child(4) .ivu-checkbox-input');
        await lookLogBtn.click();

        const addBtn = await page.waitForSelector('.ui-edit-manager-page--footer .ivu-btn.ivu-btn-primary');
        await addBtn.click();

        await page.waitFor(300000);

    }

    public async managerSettingc(page:Page){//所在分组及下级分组公司基础信息配置
        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        await page.waitFor(1000);

        const managerBtn = await page.waitForSelector('a[href="#/admin/manager"]');
        await managerBtn.click();

        await page.waitFor(5000);

        const addManagerBtn = await page.waitForSelector('.ui-manager-page--header .ivu-btn.ivu-btn-default');
        await addManagerBtn.click();

        await page.waitFor(2000);

        const selectUserBtn = await page.waitForSelector('span.placeholder');
        await selectUserBtn.click();

        await page.waitFor(2000);

        const userCheckbox = await page.waitForSelector('.user-list>li:nth-child(4) .ivu-checkbox-input');
        await userCheckbox.click();

        await page.waitFor(2000);

        const keepBtn = await page.waitForSelector('.ui-choose-base--footer.flex-row .ivu-btn.ivu-btn-primary');
        await keepBtn.click();

        await page.waitFor(2000);
        const companySetBtn = await page.waitForSelector('.ivu-checkbox-group.ivu-checkbox-default>ul>li:nth-child(5) .ivu-checkbox-input');
        await companySetBtn.click();

        const addBtn = await page.waitForSelector('.ui-edit-manager-page--footer .ivu-btn.ivu-btn-primary');
        await addBtn.click();

        await page.waitFor(300000);

    }

    public async managerSettingd(page:Page){//所在分组及下级分组应用测试应用权限
        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        await page.waitFor(1000);

        const managerBtn = await page.waitForSelector('a[href="#/admin/manager"]');
        await managerBtn.click();

        await page.waitFor(5000);

        const addManagerBtn = await page.waitForSelector('.ui-manager-page--header .ivu-btn.ivu-btn-default');
        await addManagerBtn.click();

        await page.waitFor(2000);

        const selectUserBtn = await page.waitForSelector('span.placeholder');
        await selectUserBtn.click();

        await page.waitFor(2000);

        const userCheckbox = await page.waitForSelector('.user-list>li:nth-child(5) .ivu-checkbox-input');
        await userCheckbox.click();

        await page.waitFor(2000);

        const keepBtn = await page.waitForSelector('.ui-choose-base--footer.flex-row .ivu-btn.ivu-btn-primary');
        await keepBtn.click();

        await page.waitFor(2000);

        const appCheckbox = await page.waitForSelector('.perm-settings-main-app-list>div>ul>li .ivu-checkbox');
        await appCheckbox.click();

        const addBtn = await page.waitForSelector('.ui-edit-manager-page--footer .ivu-btn.ivu-btn-primary');
        await addBtn.click();

        await page.waitFor(300000);

    }

    public async editManager(page:Page){//编辑管理员bumen2user的权限
        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        await page.waitFor(1000);

        const managerBtn = await page.waitForSelector('a[href="#/admin/manager"]');
        await managerBtn.click();

        await page.waitFor(5000);

        const editManagerBtn = await page.waitForSelector('.ivu-table-tbody>tr:last-child>td:last-child a');
        await editManagerBtn.click();

        const logCheckbox = await page.waitForSelector('.ivu-checkbox-group.ivu-checkbox-default>ul>li:nth-child(4) .ivu-checkbox');
        await logCheckbox.click();

        const addBtn = await page.waitForSelector('.ui-edit-manager-page--footer .ivu-btn.ivu-btn-primary');
        await addBtn.click();

        await page.waitFor(300000);

    }

    public async deleteManager(page:Page){//删除管理员bumen2user
        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        await page.waitFor(1000);

        const managerBtn = await page.waitForSelector('a[href="#/admin/manager"]');
        await managerBtn.click();

        await page.waitFor(5000);

        const editManagerBtn = await page.waitForSelector('.ivu-table-tbody>tr:last-child>td:last-child a');
        await editManagerBtn.click();

        await page.waitFor(5000);

        const deleteBtn = await page.waitForSelector('.ui-edit-manager-page--footer-wrapper .ivu-btn.ivu-btn-error');
        await deleteBtn.click();

        const keepBtn = await page.waitForSelector('.ivu-btn.ivu-btn-primary.ivu-btn-large');
        await keepBtn.click();

        await page.waitFor(120000);

    }

}