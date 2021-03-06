Vue.component("modal", {
    template: "#modal-template"
});

const vm = new Vue({
    el: '#vm',
    delimiters: ['[[', ']]'],
    data() {
        return {
            ninjas: [],
            loginInfo: {},
            rfidInput: '',
            showLoginModal: false,
            showWristbandModal: false,
            showSuccessModal: false,
            showErrorModal: false,
            showScanInModal: false,
            message: ''
        };
    },
    computed: {
        normalizedRfid() {
            return this.normalizeRfid(this.rfidInput);
        }
    },
    methods: {
        normalizeRfid(value) {
            if (value) {
                value = value.toLowerCase();
                let res = "";
                for (let i = 0; i < value.length; i++) {
                    if ("0123456789abcdef".indexOf(value[i]) >= 0) {
                        res += value[i];
                    }
                }
                if (res.length != 8) return '';
                return res;
            }
            return '';
        },
        successModal(message) {
            this.message = message;
            this.showSuccessModal = true;
        },
        errorModal(message) {
            this.message = message;
            this.showErrorModal = true;
        },
        signInButtonClick(ninja) {
            this.loginInfo = null;
            const url = `/api/ninjas/${ninja.studentGuid}`;
            axios.get(url)
                .then(res => {
                    console.log(res.data);
                    ninja.hasActiveWristband = res.data.hasActiveWristband;
                    this.loginInfo = ninja;
                    this.showLoginModal = true;
                })
                .catch(error => {
                    this.showLoginModal = false;
                    this.errorModal('Cannot retrieve ninja detail.')
                })
        },
        wristbandButtonClick(ninja) {
            this.loginInfo = null;
            this.rfidInput = '';
            const url = `/api/ninjas/${ninja.studentGuid}`;
            axios.get(url)
                .then((res) => {
                    console.log(res.data);
                    ninja.hasActiveWristband = res.data.hasActiveWristband;
                    this.loginInfo = ninja;
                    this.showWristbandModal = true;
                })
                .catch((error) => {
                    this.showWristbandModal = false;
                    this.errorModal('Cannot retrieve ninja detail.')
                })
        },
        scanInButtonClick() {
            this.rfidInput = '';
            this.showScanInModal = true;
        },
        login(ninja, sessionLength) {
            this.showLoginModal = false;
            const url = `/api/ninjas/${ninja.studentGuid}/login`;
            let data = {
                length: sessionLength,
                programCode: ninja.programCode,
                licenseGuid: ninja.licenseGuid
            };
            axios.post(url, data)
                .then((res) => {
                    if (res.data.hasAccess) {
                        this.successModal(`Logged in for ${sessionLength}-hour session.`);
                    } else {
                        this.errorModal(`Login failed: ${res.data.message}`);
                    }
                })
                .catch((error) => {
                    this.errorModal("Login failed!");
                })
        },
        registerWristband(ninja, rfid) {
            this.showWristbandModal = false;

            const url = `/api/ninjas/${ninja.studentGuid}/registerWristband`;
            let data = { isVirtual: rfid === 'virtual' };
            if (data.isVirtual) {
                rfid = '';
                for (let i = 0; i < 6; i++) rfid += "0123456789abcdef".charAt(Math.floor(Math.random() * 16));
                rfid += "04";
                console.log("Using a virtual rfid: " + rfid);
                data.rfid = rfid;
            } else {
                data.rfid = this.normalizeRfid(rfid);
            }
            axios.post(url, data)
                .then((res) => {
                    if (res.data.successful) {
                        this.successModal(`Wristband with RFID ${data.rfid} is successfully registered to ${ninja.name}.`);
                    } else {
                        this.errorModal(res.data.message);
                    }
                })
                .catch((error) => {
                    this.errorModal("Error registering wristband");
                });
        },
        checkWristband(rfid) {
            this.showScanInModal = false;

            const url = `/api/wristbands?rfid=${rfid}`;
            axios.get(url)
                .then((res) => {
                    console.log(res.data);
                    let found = false;
                    for (let i = 0; !found && i < this.ninjas.length; i++) {
                        if (this.ninjas[i].studentGuid === res.data.searchedMember) {
                            this.signInButtonClick(this.ninjas[i]);
                            found = true;
                        }
                    }
                    if (!found) {
                        this.errorModal(`Wristband with RFID ${data.rfid} is valid and assigned to ninja with GUID: ${res.data.searchedMember} who is inactive.`);
                    }
                })
                .catch((error) => {
                    this.errorModal(`Cannot find ninja with RFID ${rfid}.`);
                })
        },
    },
    mounted() {
        const url = "/api/ninjas";
        axios.get(url)
            .then(res => {
                this.ninjas = res.data;
                console.log(this.ninjas);
            })
            .catch(error => {
            });
    }
});
