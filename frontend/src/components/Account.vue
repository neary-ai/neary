<template>
    <div id="documents-window" class="flex flex-col gap-3 max-w-3xl overflow-y-scroll">
        <div class="p-8 pt-[5.5rem]">
            <SectionHeading section-name="Manage Account" @on-click="onBackButtonClick" />
            <div class="divide-y divide-slate-400/20">

                <div class="grid grid-cols-1 sm:grid-cols-7 py-12">
                    <div class="col-span-full sm:col-span-3 pr-6">
                        <div class="flex flex-col mb-6 sm:mb-0">
                            <div class="text-nearygray-50 font-semibold mb-2">User Profile</div>
                            <div class="text-sm text-slate-400">Information in your profile is made available to all
                                conversations.</div>
                        </div>
                    </div>
                    <div class="col-span-full sm:col-span-4 flex flex-col text-slate-400">
                        <div class="flex flex-col items-start">
                            <template v-for="(value, key) in store.userProfile">
                                <template v-if="key === 'name'">
                                    <!-- Custom template for name -->
                                    <label class="text-sm font-semibold text-field-label w-full mb-1.5">{{
                                        capitalize(key) }}</label>
                                    <TextInputField class="mb-6 max-w-xs" inputType="text"
                                        placeholderText="Enter your full name" :value="value"
                                        @updateInput="updateProfile(key, $event)" />
                                </template>
                                <template v-else-if="key === 'location'">
                                    <!-- Custom template for location -->
                                    <label class="text-sm font-semibold text-field-label w-full mb-1.5">{{
                                        capitalize(key) }}</label>
                                    <TextInputField class="mb-6 max-w-xs" inputType="text"
                                        placeholderText="Enter your location" :value="value"
                                        @updateInput="updateProfile(key, $event)" />
                                </template>
                                <template v-else-if="key === 'notes'">
                                    <!-- Custom template for notes -->
                                    <label class="text-sm font-semibold text-field-label w-full mb-1.5">{{
                                        capitalize(key) }}</label>
                                    <TextareaField class="mb-6 max-w-xs" placeholderText="Enter your notes" :value="value"
                                        @updateInput="updateProfile(key, $event)" />
                                </template>
                                <template v-else>
                                    <!-- Default template -->
                                    <label class="text-sm font-semibold text-field-label w-full mb-1.5">{{
                                        capitalize(key) }}</label>
                                    <div class="flex w-full items-center gap-3 mb-6">
                                        <TextInputField class="max-w-xs" inputType="text" placeholderText="Enter details.."
                                            :value="value" @updateInput="updateProfile(key, $event)" />
                                        <XMarkIcon @click="removeProfileField(key)"
                                            class="h-6 w-6 shrink-0 cursor-pointer" />
                                    </div>
                                </template>
                            </template>

                            <button @click="openModal();" type="button"
                                class="text-sm font-semibold leading-6 text-nearylight-100 hover:text-nearylight-100/80"><span
                                    aria-hidden="true">+</span> Add more information</button>
                        </div>
                    </div>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-7 py-12">
                    <div class="col-span-full sm:col-span-3 pr-6">
                        <div class="flex flex-col mb-6 sm:mb-0">
                            <div class="text-nearygray-50 font-semibold mb-2">Change Password</div>
                        </div>
                    </div>
                    <div class="col-span-full sm:col-span-4 flex flex-col">
                        <div class="flex flex-col items-start">
                            <label class="text-sm font-semibold text-field-label w-full mb-1.5">New Password</label>
                            <TextInputField class="mb-6 max-w-xs" inputType="password"
                                placeholderText="Enter a new password.." @updateInput="updatePassword($event)" />
                        </div>
                        <div class="flex gap-3 mt-2">
                            <Button @buttonClick="changePassword" button-type="btn-light">Save Password</Button>
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
                            <Button @buttonClick="logout" button-type="btn-light">Logout</Button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <Modal :isOpen="isOpen" @save="save" @close="close">
        <template v-slot:title>
            <h3 class="font-semibold text-lg text-field-default-foreground">Add Profile Data</h3>
        </template>
        <div class="flex-grow w-full my-5">
            <div>
                <input v-model="fieldLabel" type="text" placeholder="Field Label (e.g. Age)"
                    class="focus:ring-0 focus:border-nearyblue-300 border border-transparent rounded-md bg-nearygray-100 text-sm w-full px-3 py-2" />
                <input v-model="fieldValue" type="text" placeholder="Field Value (e.g. 40)"
                    class="focus:ring-0 focus:border-nearyblue-300 border border-transparent rounded-md bg-nearygray-100 text-sm w-full px-3 py-2" />
            </div>
        </div>
        <template v-slot:buttons>
            <Button @buttonClick="save" button-type="btn-light">Save</Button>
            <Button @buttonClick="close" button-type="btn-light">Cancel</Button>
        </template>
    </Modal>
</template>
  
<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAppStore } from '@/store/index.js';
import api from '@/services/apiService';
import Button from './common/Button.vue';
import SectionHeading from './common/SectionHeading.vue';
import TextInputField from './common/TextInputField.vue';
import TextareaField from './common/TextareaField.vue';
import Modal from './common/Modal.vue';
import Alert from './common/Alert.vue';
import { XMarkIcon } from '@heroicons/vue/20/solid';
const store = useAppStore();
const router = useRouter();

const password = ref('');
const alertData = ref({});

const capitalize = (str) => {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
};

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

const removeProfileField = async (key) => {
    delete store.userProfile[key]
    await api.updateUserProfile(store.userProfile)
}
// Modal
const updateProfile = async (key, event) => {
    store.userProfile[key] = event
    await api.updateUserProfile(store.userProfile)
}

const fieldLabel = ref(null);
const fieldValue = ref(null);

const isOpen = ref(false);

const openModal = () => {
    isOpen.value = true;
};

const save = async () => {
    isOpen.value = false;
    if (fieldLabel.value && fieldValue.value) {
        store.addProfileField({ [fieldLabel.value]: fieldValue.value })
    }
};

const close = () => {
    isOpen.value = false;
};


const onBackButtonClick = () => {
    router.go(-1);
};
</script>