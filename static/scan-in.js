Vue.component("modal", {
    template: "#modal-template"
});

const vm = new Vue({
    el: '#vm',
    delimiters: ['[[', ']]'],
    data() {
        return {
            now: new Date(),
            minutesCount: 0,
            ninjas: [],
            loginInfo: null,
            rfidInput: '',
            showLoginModal: false,
            showSuccessModal: false,
            showErrorModal: false,
            message: ''
        };
    },
    methods: {
        updateTime() {
            this.now = new Date();
            this.minutesCount++;
            if (this.minutesCount == 5) {
                this.minutesCount = 0;
                this.getNinjas();
            }
        },
        normalizeRfid(value) {
            if (value) {
                value = value.toLowerCase();
                let res = "";
                for (let i = 0; i < value.length; i++) {
                    if ("0123456789abcdef".indexOf(value[i]) >= 0) {
                        res += value[i];
                    }
                }
                if (res.length != 8 && res.length != 14) return '';
                return res;
            }
            return '';
        },
        keyHandler(event) {
            if (event.key == ';') {
                this.rfidInput = '';
            } else if ("0123456789abcdef".indexOf(event.key) >= 0) {
                this.rfidInput += event.key;
            } else if (event.key == '?') {
                this.rfidInput = this.normalizeRfid(this.rfidInput);
                console.log(`Scanned RFID: ${this.rfidInput}`);
                this.checkWristband(this.rfidInput);
                this.rfidInput = '';
            }
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
        checkWristband(rfid) {
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
        getNinjas() {
            const url = "/api/ninjas";
            axios.get(url)
                .then(res => {
                    this.ninjas = res.data;
                    console.log(this.ninjas);
                })
                .catch(error => {
                });
        },
    },
    mounted() {
        setInterval(this.updateTime, 60000);
        this.updateTime();
        this.getNinjas();
    },
    created() {
        window.addEventListener("keydown", this.keyHandler);
    }
});
