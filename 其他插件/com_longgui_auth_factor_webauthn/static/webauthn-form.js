
const {
    browserSupportsWebAuthn,
    startRegistration,
    startAuthentication,
    browserSupportsWebAuthnAutofill,
} = SimpleWebAuthnBrowser;

if (browserSupportsWebAuthn()) {
    console.log('support authwebn')
}
async function webauthnStartAuthentication(model, startConditionalUI = false) {
    try {
        console.log('start webauthn authentication')
        console.log(model)
        // const {
        //     authRequireUserVerification,
        // } = this.options;

        // Submit options
        const apiAuthOptsResp = await fetch('api/v1/com_longgui_auth_factor_webauthn/authentication/options', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username: model.username,
                config_id: model.config_id,
                // require_user_verification: authRequireUserVerification,
            }),
        });
        const authenticationOptionsJSON = await apiAuthOptsResp.json();

        if (authenticationOptionsJSON.error) {
            // this.showErrorAlert(authenticationOptionsJSON.error);
            console.log(authenticationOptionsJSON)
            return authenticationOptionsJSON;
        }

        // Start WebAuthn authentication
        const authResp = await startAuthentication(authenticationOptionsJSON, startConditionalUI);

        // Submit response
        const apiAuthVerResp = await fetch('api/v1/com_longgui_auth_factor_webauthn/authentication/verification', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username: model.username,
                config_id: model.config_id,
                response: authResp,
            }),
        });
        const verificationJSON = await apiAuthVerResp.json()

        // if (verificationJSON.verified === true) {
        //     // Reload page to display profile
        //     window.location.href = '{% url "index" %}';
        // } else {
        //     this.showErrorAlert(`Authentication failed: ${verificationJSON.error}`);
        // }
        console.log(verificationJSON)
        return verificationJSON
    } catch (ex) {
        return {
            error: '10001-31',
            message: ex.message
        }
    }
}

async function webauthnStartRegistration(model) {
    try {
        console.log('start webauthn registration')
        console.log(model)
        const apiRegOptsResp = await fetch('api/v1/com_longgui_auth_factor_webauthn/registration/options', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username: model.username,
                config_id: model.config_id,
            }),
        });
        const registrationOptionsJSON = await apiRegOptsResp.json();

        // Start WebAuthn registration
        const regResp = await startRegistration(registrationOptionsJSON);

        // Submit response
        const apiRegVerResp = await fetch('api/v1/com_longgui_auth_factor_webauthn/registration/verification', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username: model.username,
                config_id: model.config_id,
                response: regResp,
            }),
        });
        const verificationJSON = await apiRegVerResp.json()
        console.log(verificationJSON)

        return verificationJSON
    } catch (ex) {
        return {
            error: '10001-30',
            message: ex.message
        }
    }
}


async function webauthnInnerRegistration() {
    try {
        console.log('start webauthn inner registration')
        let token = localStorage.getItem('token');
        let tenant_id = localStorage.getItem('tenant_id');


        const apiInnerRegInfoResp = await fetch(`/api/v1/tenant/${tenant_id}/com_longgui_auth_factor_webauthn/registration/inner_info`, {
            method: 'GET',
            headers: { 'Authorization': `Token ${token}` },
        });
        const InnerRegistrationInfoJSON = await apiInnerRegInfoResp.json();

        let username = InnerRegistrationInfoJSON.username
        let config_id = InnerRegistrationInfoJSON.config_id

        const apiRegOptsResp = await fetch('/api/v1/com_longgui_auth_factor_webauthn/registration/options', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username: username,
                config_id: config_id,
            }),
        });
        const registrationOptionsJSON = await apiRegOptsResp.json();

        // Start WebAuthn registration
        const regResp = await startRegistration(registrationOptionsJSON);

        // Submit response
        const apiRegVerResp = await fetch('/api/v1/com_longgui_auth_factor_webauthn/registration/inner_verification', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Token ${token}` },
            body: JSON.stringify({
                username: username,
                config_id: config_id,
                response: regResp,
            }),
        });
        const verificationJSON = await apiRegVerResp.json()
        console.log(verificationJSON)

        // Display outcome
        // if (verificationJSON.verified === true) {
        //     // this.showSuccessAlert('Success! Now try to authenticate...');
        //     console.log('Success! Now try to authenticate...');
        // } else {
        //     // this.showErrorAlert(`Registration failed: ${verificationJSON.error}`);
        //     console.log(`Registration failed: ${verificationJSON.error}`);
        // }
        return verificationJSON

    } catch (ex) {
        return {
            error: '10001-30',
            message: ex.message
        }
    }
}

