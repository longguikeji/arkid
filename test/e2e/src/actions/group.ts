import {Page, launch} from 'puppeteer';

export class groupAction{
    public async groupAddress(page:Page){
        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        const groupBtn = await page.waitForSelector('.header-middle a[href="#/admin/group"]');
        await groupBtn.click();

        await page.waitFor(5000);
 
    }

    public async addGroup(page:Page, groupName:string){
        const addGroupBtn = await page.waitForSelector('div.flex-col.ui-group-page-side.ui-group-page-tree-group > div.subtitle > div > span');
        await addGroupBtn.click();

        await page.waitFor(2000);

        const groupNameINput = await page.waitForSelector('.ivu-drawer-body .ivu-input.ivu-input-default');
        await groupNameINput.type(groupName);

        const visibleBtn = await page.waitForSelector('.ivu-drawer-wrap.ui-edit-group > div > div > div > form > div:nth-child(3) > div > div > div.ivu-select-selection');
        await visibleBtn.click();

        const hiddenBtn = await page.waitForSelector('.ivu-form-item-content .ivu-select-dropdown-list>li:nth-child(4)');
        await hiddenBtn.click();

        const addBtn = await page.waitForSelector('.drawer-footer.flex-row.flex-auto .ivu-btn.ivu-btn-primary');
        await addBtn.click();

        await page.waitFor(3000);

    }

    public async editGroup(page:Page, groupName:string){
        const group2Btn = await page.waitForSelector('.ui-group-tree.ivu-tree>ul:nth-child(2)');
        await group2Btn.click();

        const editBtn = await page.waitForSelector('div.ui-group-page-detail-header.flex-row > button:nth-child(2)');
        await editBtn.click();

        await page.waitFor(2000);

        const groupNameINput = await page.waitForSelector('.ivu-drawer-body .ivu-input.ivu-input-default');
        await groupNameINput.type(groupName);

        const visibleBtn = await page.waitForSelector('.ivu-drawer-wrap.ui-edit-group > div > div > div > form > div:nth-child(3) > div > div > div.ivu-select-selection');
        await visibleBtn.click();

        const hiddenBtn = await page.waitForSelector('.ivu-form-item-content .ivu-select-dropdown-list>li:nth-child(2)');
        await hiddenBtn.click();

        const addBtn = await page.waitForSelector('.drawer-footer.flex-row.flex-auto .ivu-btn.ivu-btn-primary');
        await addBtn.click();

        await page.waitFor(2000);
    }

    public async addLowGroup(page:Page, groupName:string){
        const addGroupBtn = await page.waitForSelector('.ui-group-page-detail-header.flex-row>button:nth-child(3)');
        await addGroupBtn.click();

        await page.waitFor(2000);

        const groupNameINput = await page.waitForSelector('.ivu-drawer-body .ivu-input.ivu-input-default');
        await groupNameINput.type(groupName);

        // const hiddenBtn = await page.waitForSelector('.ivu-form-item-content .ivu-select-dropdown-list>li:nth-child(2)');
        // await hiddenBtn.click();

        const addBtn = await page.waitForSelector('.drawer-footer.flex-row.flex-auto .ivu-btn.ivu-btn-primary');
        await addBtn.click();

        await page.waitFor(2000);

    }

    public async addUser(page:Page, username:string, name:string, password:string, repassword:string){

        const addUserBtn = await page.waitForSelector('.ui-user-list .flex-row.flex-auto .ivu-btn.ivu-btn-primary');
        await addUserBtn.click();

        const usernameInput = await page.waitForSelector('input[placeholder="请输入 用户名"]');
        await usernameInput.type(username);

        const nameInput = await page.waitForSelector('input[placeholder="请输入 姓名"]');
        await nameInput.type(name);

        const pwdBtn = await page.waitForSelector('.ivu-form-item-content .ivu-btn.ivu-btn-primary');
        await pwdBtn.click();

        await page.waitFor(1000);

        const pwdInput = await page.waitForSelector('input[placeholder="请添加新登录密码"]');
        await pwdInput.type(password);

        const repwdInput = await page.waitForSelector('input[placeholder="再次输入登录密码"]');
        await repwdInput.type(repassword);

        const primaryBtn= await page.waitForSelector('div.ivu-modal-footer > div > button.ivu-btn.ivu-btn-primary');
        await primaryBtn.click();

        await page.waitFor(2000);

        const addBtn = await page.waitForSelector('.drawer-footer.flex-row.flex-auto .ivu-btn.ivu-btn-primary');
        await addBtn.click();

        await page.waitFor(2000);

    }

    public async editUser(page:Page, name:string, password:string, repassword:string){
       
        const editUserBtn = await page.waitForSelector('.ivu-table-cell .table-btn');
        await editUserBtn.click();
        
        const nameInput = await page.waitForSelector('input[placeholder="请输入 姓名"]');
        await nameInput.type(name);

        await page.waitFor(1000);

        const pwdBtn = await page.waitForSelector('.ivu-form-item-content .ivu-btn.ivu-btn-primary');
        await pwdBtn.click();

        await page.waitFor(1000);

        const pwdInput = await page.waitForSelector('input[placeholder="请添加新登录密码"]');
        await pwdInput.type(password);

        const repwdInput = await page.waitForSelector('input[placeholder="再次输入登录密码"]');
        await repwdInput.type(repassword);

        const primaryBtn= await page.waitForSelector('div.ivu-modal-footer > div > button.ivu-btn.ivu-btn-primary');
        await primaryBtn.click();

        await page.waitFor(2000);

        const addBtn = await page.waitForSelector('.drawer-footer.flex-row.flex-auto .ivu-btn.ivu-btn-primary');
        await addBtn.click();

        await page.waitFor(2000);

    }

    public async editUserGroup(page:Page, search:string ){
        const groupBtn = await page.waitForSelector('.ui-group-tree.ivu-tree>ul:nth-child(2)');
        await groupBtn.click();

        await page.waitFor(2000);

        const userCheckbox = await page.waitForSelector('.ivu-checkbox-input');
        await userCheckbox.click();

        const editGroupBtn = await page.waitForSelector('.ui-user-list .flex-row.flex-auto>button:nth-child(4)');
        await editGroupBtn.click();

        await page.waitFor(2000);

        const searchInput = await page.waitForSelector('div.ui-choose-base--middle > div > div.search.ivu-input-wrapper.ivu-input-wrapper-default.ivu-input-type > input');
        await searchInput.type(search);

        await page.waitFor(1000);

        const groupCheckbox = await page.waitForSelector('div.ivu-modal-body > div > div.ui-choose-base--middle > div > ul > li > label > span.ivu-checkbox > input');
        await groupCheckbox.click();

        const keepBtn = await page.waitForSelector('.ui-choose-base--footer.flex-row .ivu-btn.ivu-btn-primary');
        await keepBtn.click();

        await page.waitFor(3000);

    }

    public async removeUserGroup(page:Page){

        const groupUserBtn = await page.waitForSelector('.ui-group-tree.ivu-tree>ul:nth-child(3)>li>div');
        await groupUserBtn.click(); 

        await page.waitFor(2000);

        const userCheckbox = await page.waitForSelector('tbody > tr:nth-child(2) > td.ivu-table-column-center > div > label');
        await userCheckbox.click();

        const removeGroupBtn = await page.waitForSelector('.ui-user-list .flex-row.flex-auto>button:nth-child(5)');
        await removeGroupBtn.click();

        await page.waitFor(3000);

    }

    public async deleteUserGroup(page:Page){
        
        const groupUserBtn = await page.waitForSelector('.ui-group-tree.ivu-tree>ul:nth-child(2) .ui-tree-item-title span');
        await groupUserBtn.click();

        const userCheckbox = await page.waitForSelector('.ivu-table-tbody>tr:last-child .ivu-checkbox-input');
        await userCheckbox.click();

        const deleteGroupBtn = await page.waitForSelector('.ui-user-list .flex-row.flex-auto>button:nth-child(7)');
        await deleteGroupBtn.click();
    }

    public async addPersonalGroup(page:Page, groupName:string){
        const addBtn = await page.waitForSelector('.meta-node-title.custom-title .add');
        await addBtn.click();

        const nameInput = await page.waitForSelector('input[placeholder="输入名称"]');
        await nameInput.type(groupName);

        const keepBtn = await page.waitForSelector('.search-input>div>span:last-child');
        await keepBtn.click();

        await page.waitFor(3000);
    }

    public async personalUserGroup(page:Page, groupName:string){
        const directUserBtn = await page.waitForSelector('.custom-list>li:last-child');
        await directUserBtn.click();

        await page.waitFor(1000);

        const addDirectUserBtn = await page.waitForSelector('.subtitle-wrapper .add');
        await addDirectUserBtn.click();

        await page.waitFor(1000);

        const directUserInput = await page.waitForSelector('div.ivu-drawer-wrap.ui-edit-group > div > div > div > form > div.ivu-form-item.ivu-form-item-required > div > div > input');
        await directUserInput.type(groupName);

        // const visibleBtn = await page.waitForSelector('.ivu-select-placeholder');
        // await visibleBtn.click();

        // const hiddenBtn = await page.waitForSelector('.ivu-select-dropdown-list>li:nth-child(4)');
        // await hiddenBtn.click();

        const addBtn = await page.waitForSelector('.drawer-footer.flex-row.flex-auto .ivu-btn.ivu-btn-primary');
        await addBtn.click();

        await page.waitFor(2000);

    }

    public async editPerGroup(page:Page, groupName:string){
        const directUserBtn = await page.waitForSelector('.custom-list>li:nth-child(1)');
        await directUserBtn.click();

        await page.waitFor(2000);

        const editBtn = await page.waitForSelector('.ui-group-page-detail-header.flex-row .ivu-btn.ivu-btn-default');
        await editBtn.click();

        await page.waitFor(2000);

        const groupNameINput = await page.waitForSelector('.ivu-drawer-body .ivu-input.ivu-input-default');
        await groupNameINput.type(groupName);

        const visibleBtn = await page.waitForSelector('form > div:nth-child(3) > div > div > div.ivu-select-selection > div');
        await visibleBtn.click();

        const hiddenBtn = await page.waitForSelector('.ivu-form-item-content .ivu-select-dropdown-list>li:nth-child(4)');
        await hiddenBtn.click();

        const addBtn = await page.waitForSelector('.drawer-footer.flex-row.flex-auto .ivu-btn.ivu-btn-primary');
        await addBtn.click();

        await page.waitFor(2000);
    }

    public async addPerLowGroup(page:Page, groupName:string){
        const directUserBtn = await page.waitForSelector('.custom-list>li');
        await directUserBtn.click();

        const addGroupBtn = await page.waitForSelector('.ui-group-page-detail-header.flex-row>button:nth-child(3)');
        await addGroupBtn.click();

        await page.waitFor(2000);

        const groupNameINput = await page.waitForSelector('.ivu-drawer-body .ivu-input.ivu-input-default');
        await groupNameINput.type(groupName);

        const addBtn = await page.waitForSelector('.drawer-footer.flex-row.flex-auto .ivu-btn.ivu-btn-primary');
        await addBtn.click();

        await page.waitFor(2000);

    }

    public async addPerUser(page:Page, username:string, name:string, password:string, repassword:string){
        const directUserBtn = await page.waitForSelector('.custom-list>li:nth-child(1)');
        await directUserBtn.click();

        await page.waitFor(2000);

        const addUserBtn = await page.waitForSelector('.ui-user-list .flex-row.flex-auto .ivu-btn.ivu-btn-primary');
        await addUserBtn.click();

        const usernameInput = await page.waitForSelector('input[placeholder="请输入 用户名"]');
        await usernameInput.type(username);

        const nameInput = await page.waitForSelector('input[placeholder="请输入 姓名"]');
        await nameInput.type(name);

        const pwdBtn = await page.waitForSelector('.ivu-form-item-content .ivu-btn.ivu-btn-primary');
        await pwdBtn.click();

        await page.waitFor(1000);

        const pwdInput = await page.waitForSelector('input[placeholder="请添加新登录密码"]');
        await pwdInput.type(password);

        const repwdInput = await page.waitForSelector('input[placeholder="再次输入登录密码"]');
        await repwdInput.type(repassword);

        const primaryBtn= await page.waitForSelector('div.ivu-modal-footer > div > button.ivu-btn.ivu-btn-primary');
        await primaryBtn.click();

        await page.waitFor(2000);

        const addBtn = await page.waitForSelector('.drawer-footer.flex-row.flex-auto .ivu-btn.ivu-btn-primary');
        await addBtn.click();

        await page.waitFor(2000);

    }

    public async editPerUser(page:Page, name:string, password:string, repassword:string){
        const directUserBtn = await page.waitForSelector('.custom-list>li:nth-child(1)');
        await directUserBtn.click();

        await page.waitFor(1000);

        const editUserBtn = await page.waitForSelector('.ivu-table-cell .table-btn');
        await editUserBtn.click();

        await page.waitFor(2000);
        
        const nameInput = await page.waitForSelector('input[placeholder="请输入 姓名"]');
        await nameInput.type(name);

        const pwdBtn = await page.waitForSelector('.ivu-form-item-content .ivu-btn.ivu-btn-primary');
        await pwdBtn.click();

        await page.waitFor(1000);

        const pwdInput = await page.waitForSelector('input[placeholder="请添加新登录密码"]');
        await pwdInput.type(password);

        const repwdInput = await page.waitForSelector('input[placeholder="再次输入登录密码"]');
        await repwdInput.type(repassword);

        const primaryBtn= await page.waitForSelector('div.ivu-modal-footer > div > button.ivu-btn.ivu-btn-primary');
        await primaryBtn.click();

        await page.waitFor(2000);

        const addBtn = await page.waitForSelector('.drawer-footer.flex-row.flex-auto .ivu-btn.ivu-btn-primary');
        await addBtn.click();

        await page.waitFor(2000);
    }

    public async groupPower(page:Page, search:string){
        const groupBtn = await page.waitForSelector('.ui-group-tree.ivu-tree>ul:nth-child(2)');
        await groupBtn.click();

        await page.waitFor(2000);
        
        const powerBtn = await page.waitForSelector('.ivu-btn.ivu-btn-primary');
        await powerBtn.click();

        await page.waitFor(2000);

        const appNameInput = await page.waitForSelector('input[placeholder="搜索应用"]');
        await appNameInput.type(search);

        await page.waitFor(2000);

        const appBtn = await page.waitForSelector('.result-list>li');
        await appBtn.click();

        await page.waitFor(6000);

        const setBtn = await page.waitForSelector('div.ivu-table-body > table > tbody > tr > td:nth-child(3) > div > div > div > div');
        await setBtn.click();

        const yesBtn = await page.waitForSelector('.ivu-select-dropdown.ivu-dropdown-transfer .ivu-dropdown-menu>li');
        await yesBtn.click();

        await page.waitFor(300000);

    }

    public async personalGroupPower(page:Page, search:string){
        const groupBtn = await page.waitForSelector('.custom-list>li');
        await groupBtn.click();

        await page.waitFor(2000);
        
        const powerBtn = await page.waitForSelector('.ivu-btn.ivu-btn-primary');
        await powerBtn.click();

        const appNameInput = await page.waitForSelector('input[placeholder="搜索应用"]');
        await appNameInput.type(search);

        await page.waitFor(2000);

        const appBtn = await page.waitForSelector('.result-list>li');
        await appBtn.click();

        await page.waitFor(6000);

        const setBtn = await page.waitForSelector('div.ivu-table-body > table > tbody > tr > td:nth-child(3) > div > div > div > div');
        await setBtn.click();

        const yesBtn = await page.waitForSelector('.ivu-select-dropdown.ivu-dropdown-transfer .ivu-dropdown-menu>li');
        await yesBtn.click();

        await page.waitFor(300000);

    }

}