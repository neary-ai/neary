<template>
    <div id="documents-window" class="flex flex-col gap-3 max-w-3xl overflow-y-scroll">
        <div class="p-8 pt-[5.5rem]">
            <SectionHeading section-name="Manage Account" @on-click="onBackButtonClick" />
            <div class="divide-y divide-slate-400/20">
                <div class="grid grid-cols-1 sm:grid-cols-7 py-12">
                    <div class="col-span-full sm:col-span-3 pr-6">
                        <div class="flex flex-col mb-6 sm:mb-0">
                            <div class="text-nearygray-50 font-semibold mb-2">Change Password</div>
                            
                        </div>
                    </div>
                    <div class="col-span-full sm:col-span-4 flex flex-col">
                        <div class="flex flex-col items-start">
                            <label class="text-sm font-semibold text-field-label w-full mb-1.5">New Password</label>
                            <TextInputField class="mb-6 max-w-xs" inputType="password" placeholderText="Enter a new password" @updateInput="updatePassword($event)" />
                        </div>
                        <div class="flex gap-3 mt-2">
                            <Button @buttonClick="changePassword" button-type="btn-pink">Save Password</Button>
                            <Alert section="change_password" v-model="alertData" />
                        </div>
                    </div>
                </div>
                <div class="grid grid-cols-1 sm:grid-cols-7 py-12">
                    <div class="col-span-full sm:col-span-3 pr-6">
                        <div class="flex flex-col mb-6 sm:mb-0">
                            <div class="text-nearygray-50 font-semibold mb-2">Account Actions</div>
                            <div class="text-sm text-slate-400"></div>
                        </div>
                    </div>
                    <div class="col-span-full sm:col-span-4 flex flex-col text-slate-400">
                        <div class="flex flex-col items-start">
                            <Button @buttonClick="logout" button-type="btn-pink">Logout</Button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
  
<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import api from '@/services/apiService';
import Button from './common/Button.vue';
import SectionHeading from './common/SectionHeading.vue';
import TextInputField from './common/TextInputField.vue';
import Alert from './common/Alert.vue';


const router = useRouter();
const password = ref('');
const alertData = ref({});

const updatePassword = (newPassword) => {
    password.value = newPassword;
};

const changePassword = async () => {
    const response = await api.changeUserPassword(password.value);

    if (response.status == 200) {
        alertData.value = { alertType: "success", alertMessage: "Password changed!", section: "change_password" };
    } else {
        alertData.value = { alertType: "error", alertMessage: "We had trouble saving your new password.", section: "change_password" };
    }
};

const logout = async () => {
    await api.logoutUser();
    router.push('/login');
}

const onBackButtonClick = () => {
    router.go(-1);
};
</script>