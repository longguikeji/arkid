import {Page, launch} from 'puppeteer';

export class groupAction{
    public async groupAddress(page:Page){
        const manageBtn = await page.waitForSelector('.workspace-btn.ivu-btn.ivu-btn-default');
        await manageBtn.click();

        const groupBtn = await page.waitForSelector('.header-middle a[href="#/admin/group"]');
        await groupBtn.click();
 
    }

    public async addGroup(page:Page, groupName:string){
        const addGroupBtn = await page.waitForSelector('.subtitle-wrapper .add');
        await addGroupBtn.click();

        const groupNameINput = await page.waitForSelector('.ivu-drawer-body .ivu-input.ivu-input-default');
        await groupNameINput.type(groupName);

        const visibleBtn = await page.waitForSelector('.ivu-select-placeholder');
        await visibleBtn.click();

        const hiddenBtn = await page.waitForSelector('.ivu-form-item-content .ivu-select-dropdown-list>li:nth-child(4)');
        await hiddenBtn.click();

        const addBtn = await page.waitForSelector('.drawer-footer.flex-row.flex-auto .ivu-btn.ivu-btn-primary');
        await addBtn.click();

    }

    public async editGroup(page:Page, groupName:string){
        const editBtn = await page.waitForSelector('.ui-group-page-detail-header.flex-row .ivu-btn.ivu-btn-default');
        await editBtn.click();

        const groupNameINput = await page.waitForSelector('.ivu-drawer-body .ivu-input.ivu-input-default');
        await groupNameINput.type(groupName);

        const hiddenBtn = await page.waitForSelector('.ivu-form-item-content .ivu-select-dropdown-list>li:nth-child(2)');
        await hiddenBtn.click();

        const addBtn = await page.waitForSelector('.drawer-footer.flex-row.flex-auto .ivu-btn.ivu-btn-primary');
        await addBtn.click();
    }

    public async addLowGroup(page:Page, groupName:string){
        const addGroupBtn = await page.waitForSelector('.ui-group-page-detail-header.flex-row>button:nth-child(3)');
        await addGroupBtn.click();

        const groupNameINput = await page.waitForSelector('.ivu-drawer-body .ivu-input.ivu-input-default');
        await groupNameINput.type(groupName);

        // const hiddenBtn = await page.waitForSelector('.ivu-form-item-content .ivu-select-dropdown-list>li:nth-child(2)');
        // await hiddenBtn.click();

        const addBtn = await page.waitForSelector('.drawer-footer.flex-row.flex-auto .ivu-btn.ivu-btn-primary');
        await addBtn.click();

    }

    public async addUser(page:Page, username:string, name:string, password:string, repassword:string){

        const addUserBtn = await page.waitForSelector('.ui-user-list .flex-row.flex-auto .ivu-btn.ivu-btn-primary');
        await addUserBtn.click();

        const usernameInput = await page.waitForSelector('input[placeholder="请输入 用户名"]');
        usernameInput.type(username);

        const nameInput = await page.waitForSelector('input[placeholder="请输入 姓名"]');
        await nameInput.type(name);

        const pwdBtn = await page.waitForSelector('.ivu-form-item-content .ivu-btn.ivu-btn-primary');
        await pwdBtn.click();

        const pwdInput = await page.waitForSelector('input[placeholder="请添加新登录密码"]');
        await pwdInput.type(password);

        const repwdInput = await page.waitForSelector('input[placeholder="再次输入登录密码"]');
        await repwdInput.type(repassword);

        const primaryBtn= await page.waitForSelector('.ivu-modal-footer .ivu-btn.ivu-btn-primary');
        await primaryBtn.click();

        const addBtn = await page.waitForSelector('.drawer-footer.flex-row.flex-auto .ivu-btn.ivu-btn-primary');
        await addBtn.click();

    }

    public async editUser(page:Page, name:string, password:string, repassword:string){

        const editUserBtn = await page.waitForSelector('.ivu-table-cell .table-btn');
        await editUserBtn.click();
        
        const nameInput = await page.waitForSelector('input[placeholder="请输入 姓名"]');
        await nameInput.type(name);

        const pwdBtn = await page.waitForSelector('.ivu-form-item-content .ivu-btn.ivu-btn-primary');
        await pwdBtn.click();

        const pwdInput = await page.waitForSelector('input[placeholder="请添加新登录密码"]');
        await pwdInput.type(password);

        const repwdInput = await page.waitForSelector('input[placeholder="再次输入登录密码"]');
        await repwdInput.type(repassword);

        const primaryBtn= await page.waitForSelector('.ivu-modal-footer .ivu-btn.ivu-btn-primary');
        await primaryBtn.click();

        const addBtn = await page.waitForSelector('.drawer-footer.flex-row.flex-auto .ivu-btn.ivu-btn-primary');
        await addBtn.click();

    }

    public async editUserGroup(page:Page, search:string ){
        const userCheckbox = await page.waitForSelector('.ivu-checkbox-input');
        await userCheckbox.click();

        const editGroupBtn = await page.waitForSelector('.ui-user-list .flex-row.flex-auto>button:nth-child(4)');
        await editGroupBtn.click();

        const searchInput = await page.waitForSelector('input[placeholder="搜索"]');
        await searchInput.type(search);

        const groupCheckbox = await page.waitForSelector('.ivu-checkbox-input');
        await groupCheckbox.click();

        const keepBtn = await page.waitForSelector('.ui-choose-base--footer.flex-row .ivu-btn.ivu-btn-primary');
        await keepBtn.click();

    }

    public async removeUserGroup(page:Page){

        const groupUserBtn = await page.waitForSelector('.ui-group-tree.ivu-tree>ul:nth-child(2) .ui-tree-item-title span');
        await groupUserBtn.click(); 

        const userCheckbox = await page.waitForSelector('.ivu-table-tbody>tr:last-child .ivu-checkbox-input');
        await userCheckbox.click();

        const removeGroupBtn = await page.waitForSelector('.ui-user-list .flex-row.flex-auto>button:nth-child(5)');
        await removeGroupBtn.click();

    }

    public async deleteUserGroup(page:Page){
        
        const groupUserBtn = await page.waitForSelector('.ui-group-tree.ivu-tree>ul:nth-child(2) .ui-tree-item-title span');
        await groupUserBtn.click();

        const userCheckbox = await page.waitForSelector('.ivu-table-tbody>tr:last-child .ivu-checkbox-input');
        await userCheckbox.click();

        const deleteGroupBtn = await page.waitForSelector('.ui-user-list .flex-row.flex-auto>button:nth-child(7)');
        await deleteGroupBtn.click();
    }

    public async directUserGroup(page:Page, groupName:string){
        const directUserBtn = await page.waitForSelector('.flex-row.flex-auto.ui-group-meta-page .default-list>li:nth-child(2)');
        await directUserBtn.click();

        const addDirectUserBtn = await page.waitForSelector('.subtitle-wrapper .add');
        await addDirectUserBtn.click();

        const directUserInput = await page.waitForSelector('input[placeholder="请输入一账通-直属成员名称"]');
        await directUserInput.type(groupName);

        const visibleBtn = await page.waitForSelector('.ivu-select-placeholder');
        await visibleBtn.click();

        const hiddenBtn = await page.waitForSelector('.ivu-select-dropdown-list>li:nth-child(4)');
        await hiddenBtn.click();

        const addBtn = await page.waitForSelector('.drawer-footer.flex-row.flex-auto .ivu-btn.ivu-btn-primary');
        await addBtn.click();

    }

    public async editDirGroup(page:Page, groupName:string){
        const directUserBtn = await page.waitForSelector('.flex-row.flex-auto.ui-group-meta-page .default-list>li:nth-child(2)');
        await directUserBtn.click();

        const editBtn = await page.waitForSelector('.ui-group-page-detail-header.flex-row .ivu-btn.ivu-btn-default');
        await editBtn.click();

        const groupNameINput = await page.waitForSelector('.ivu-drawer-body .ivu-input.ivu-input-default');
        await groupNameINput.type(groupName);

        const visibleBtn = await page.waitForSelector('.ivu-icon.ivu-icon-ios-arrow-down.ivu-select-arrow');
        await visibleBtn.click();

        const hiddenBtn = await page.waitForSelector('.ivu-form-item-content .ivu-select-dropdown-list>li:nth-child(1)');
        await hiddenBtn.click();

        const addBtn = await page.waitForSelector('.drawer-footer.flex-row.flex-auto .ivu-btn.ivu-btn-primary');
        await addBtn.click();
    }

    public async addDirLowGroup(page:Page, groupName:string){
        const directUserBtn = await page.waitForSelector('.flex-row.flex-auto.ui-group-meta-page .default-list>li:nth-child(2)');
        await directUserBtn.click();

        const addGroupBtn = await page.waitForSelector('.ui-group-page-detail-header.flex-row>button:nth-child(3)');
        await addGroupBtn.click();

        const groupNameINput = await page.waitForSelector('.ivu-drawer-body .ivu-input.ivu-input-default');
        await groupNameINput.type(groupName);

        const addBtn = await page.waitForSelector('.drawer-footer.flex-row.flex-auto .ivu-btn.ivu-btn-primary');
        await addBtn.click();

    }

    public async addDirUser(page:Page, username:string, name:string, password:string, repassword:string){
        const directUserBtn = await page.waitForSelector('.flex-row.flex-auto.ui-group-meta-page .default-list>li:nth-child(2)');
        await directUserBtn.click();

        const addUserBtn = await page.waitForSelector('.ui-user-list .flex-row.flex-auto .ivu-btn.ivu-btn-primary');
        await addUserBtn.click();

        const usernameInput = await page.waitForSelector('input[placeholder="请输入 用户名"]');
        usernameInput.type(username);

        const nameInput = await page.waitForSelector('input[placeholder="请输入 姓名"]');
        await nameInput.type(name);

        const pwdBtn = await page.waitForSelector('.ivu-form-item-content .ivu-btn.ivu-btn-primary');
        await pwdBtn.click();

        const pwdInput = await page.waitForSelector('input[placeholder="请添加新登录密码"]');
        await pwdInput.type(password);

        const repwdInput = await page.waitForSelector('input[placeholder="再次输入登录密码"]');
        await repwdInput.type(repassword);

        const primaryBtn= await page.waitForSelector('.ivu-modal-footer .ivu-btn.ivu-btn-primary');
        await primaryBtn.click();

        const addBtn = await page.waitForSelector('.drawer-footer.flex-row.flex-auto .ivu-btn.ivu-btn-primary');
        await addBtn.click();

    }

    public async editDirUser(page:Page, name:string, password:string, repassword:string){
        const directUserBtn = await page.waitForSelector('.flex-row.flex-auto.ui-group-meta-page .default-list>li:nth-child(2)');
        await directUserBtn.click();

        const editUserBtn = await page.waitForSelector('.ivu-table-cell .table-btn');
        await editUserBtn.click();
        
        const nameInput = await page.waitForSelector('input[placeholder="请输入 姓名"]');
        await nameInput.type(name);

        const pwdBtn = await page.waitForSelector('.ivu-form-item-content .ivu-btn.ivu-btn-primary');
        await pwdBtn.click();

        const pwdInput = await page.waitForSelector('input[placeholder="请添加新登录密码"]');
        await pwdInput.type(password);

        const repwdInput = await page.waitForSelector('input[placeholder="再次输入登录密码"]');
        await repwdInput.type(repassword);

        const primaryBtn= await page.waitForSelector('.ivu-modal-footer .ivu-btn.ivu-btn-primary');
        await primaryBtn.click();

        const addBtn = await page.waitForSelector('.drawer-footer.flex-row.flex-auto .ivu-btn.ivu-btn-primary');
        await addBtn.click();

    }

    public async editDirUserGroup(page:Page, search:string ){
        const directUserBtn = await page.waitForSelector('.flex-row.flex-auto.ui-group-meta-page .default-list>li:nth-child(2)');
        await directUserBtn.click();

        const userCheckbox = await page.waitForSelector('.ivu-checkbox-input');
        await userCheckbox.click();

        const editGroupBtn = await page.waitForSelector('.ui-user-list .flex-row.flex-auto>button:nth-child(4)');
        await editGroupBtn.click();

        const searchInput = await page.waitForSelector('input[placeholder="搜索"]');
        await searchInput.type(search);

        const groupCheckbox = await page.waitForSelector('.ivu-checkbox-input');
        await groupCheckbox.click();

        const keepBtn = await page.waitForSelector('.ui-choose-base--footer.flex-row .ivu-btn.ivu-btn-primary');
        await keepBtn.click();

    }

    public async addPersonalGroup(page:Page, groupName:string){
        const addBtn = await page.waitForSelector('.meta-node-title.custom-title .add');
        await addBtn.click();

        const nameInput = await page.waitForSelector('input[placeholder="输入名称"]');
        await nameInput.type(groupName);

        const keepBtn = await page.waitForSelector('.search-input>div>span:last-child');
        await keepBtn.click();
    }

    public async personalUserGroup(page:Page, groupName:string){
        const directUserBtn = await page.waitForSelector('.custom-list>li');
        await directUserBtn.click();

        const addDirectUserBtn = await page.waitForSelector('.subtitle-wrapper .add');
        await addDirectUserBtn.click();

        const directUserInput = await page.waitForSelector('input[placeholder="请输入一账通-部门名称"]');
        await directUserInput.type(groupName);

        const visibleBtn = await page.waitForSelector('.ivu-select-placeholder');
        await visibleBtn.click();

        const hiddenBtn = await page.waitForSelector('.ivu-select-dropdown-list>li:nth-child(4)');
        await hiddenBtn.click();

        const addBtn = await page.waitForSelector('.drawer-footer.flex-row.flex-auto .ivu-btn.ivu-btn-primary');
        await addBtn.click();

    }

    public async editPerGroup(page:Page, groupName:string){
        const directUserBtn = await page.waitForSelector('.custom-list>li');
        await directUserBtn.click();

        const editBtn = await page.waitForSelector('.ui-group-page-detail-header.flex-row .ivu-btn.ivu-btn-default');
        await editBtn.click();

        const groupNameINput = await page.waitForSelector('.ivu-drawer-body .ivu-input.ivu-input-default');
        await groupNameINput.type(groupName);

        const visibleBtn = await page.waitForSelector('.ivu-icon.ivu-icon-ios-arrow-down.ivu-select-arrow');
        await visibleBtn.click();

        const hiddenBtn = await page.waitForSelector('.ivu-form-item-content .ivu-select-dropdown-list>li:nth-child(1)');
        await hiddenBtn.click();

        const addBtn = await page.waitForSelector('.drawer-footer.flex-row.flex-auto .ivu-btn.ivu-btn-primary');
        await addBtn.click();
    }

    public async addPerLowGroup(page:Page, groupName:string){
        const directUserBtn = await page.waitForSelector('.custom-list>li');
        await directUserBtn.click();

        const addGroupBtn = await page.waitForSelector('.ui-group-page-detail-header.flex-row>button:nth-child(3)');
        await addGroupBtn.click();

        const groupNameINput = await page.waitForSelector('.ivu-drawer-body .ivu-input.ivu-input-default');
        await groupNameINput.type(groupName);

        const addBtn = await page.waitForSelector('.drawer-footer.flex-row.flex-auto .ivu-btn.ivu-btn-primary');
        await addBtn.click();

    }

    public async addPerUser(page:Page, username:string, name:string, password:string, repassword:string){
        const directUserBtn = await page.waitForSelector('.custom-list>li');
        await directUserBtn.click();

        const addUserBtn = await page.waitForSelector('.ui-user-list .flex-row.flex-auto .ivu-btn.ivu-btn-primary');
        await addUserBtn.click();

        const usernameInput = await page.waitForSelector('input[placeholder="请输入 用户名"]');
        usernameInput.type(username);

        const nameInput = await page.waitForSelector('input[placeholder="请输入 姓名"]');
        await nameInput.type(name);

        const pwdBtn = await page.waitForSelector('.ivu-form-item-content .ivu-btn.ivu-btn-primary');
        await pwdBtn.click();

        const pwdInput = await page.waitForSelector('input[placeholder="请添加新登录密码"]');
        await pwdInput.type(password);

        const repwdInput = await page.waitForSelector('input[placeholder="再次输入登录密码"]');
        await repwdInput.type(repassword);

        const primaryBtn= await page.waitForSelector('.ivu-modal-footer .ivu-btn.ivu-btn-primary');
        await primaryBtn.click();

        const addBtn = await page.waitForSelector('.drawer-footer.flex-row.flex-auto .ivu-btn.ivu-btn-primary');
        await addBtn.click();

    }

    public async editPerUser(page:Page, name:string, password:string, repassword:string){
        const directUserBtn = await page.waitForSelector('.custom-list>li');
        await directUserBtn.click();

        const editUserBtn = await page.waitForSelector('.ivu-table-cell .table-btn');
        await editUserBtn.click();
        
        const nameInput = await page.waitForSelector('input[placeholder="请输入 姓名"]');
        await nameInput.type(name);

        const pwdBtn = await page.waitForSelector('.ivu-form-item-content .ivu-btn.ivu-btn-primary');
        await pwdBtn.click();

        const pwdInput = await page.waitForSelector('input[placeholder="请添加新登录密码"]');
        await pwdInput.type(password);

        const repwdInput = await page.waitForSelector('input[placeholder="再次输入登录密码"]');
        await repwdInput.type(repassword);

        const primaryBtn= await page.waitForSelector('.ivu-modal-footer .ivu-btn.ivu-btn-primary');
        await primaryBtn.click();

        const addBtn = await page.waitForSelector('.drawer-footer.flex-row.flex-auto .ivu-btn.ivu-btn-primary');
        await addBtn.click();

    }

}