<template>
    <div class="font-bold text-nearylight-200 mt-12">
        Connected Integrations
    </div>
    <div class="mt-6 space-y-4">
        <template v-for="integration in integrations" :key="integration.id">
        <Card v-if="integration.is_integrated">
            <template v-slot:icon>
                <div class="flex items-center justify-center h-9 w-9 rounded shadow bg-neutral-100 mt-0.5">
                    <Icon icon="mdi:transit-connection-variant" class="text-nearylight-100 w-5 h-5" />
                </div>
            </template>
            <div class="leading-7">
                <div class="text-field-default-foreground text-sm font-medium">{{ integration.display_name }}
                </div>
                <div class="text-sm text-nearygray-400"></div>
            </div>
            <template v-slot:button>
                <Button v-if="integration.is_integrated" @click="disconnectIntegration(integration)"
                    button-type="btn-outline-light"
                    :class="['bg-nearyblue-50 text-nearygray-200 w-full sm:w-24 shrink-0 px-3 py-2 text-sm rounded']">
                    Disconnect
                </Button>
                <Button v-else @click="connectIntegration(integration)" button-type="btn-light"
                    :class="['w-full sm:w-24 shrink-0 px-3 py-2 text-sm rounded']">
                    Connect
                </Button>
            </template>
        </Card>
        </template>
    </div>
    <div class="font-bold text-nearylight-200 mt-12">
        Available Integrations
    </div>
    <div class="mt-6 space-y-4">
        <template v-for="integration in integrations" :key="integration.id">
        <Card v-if="!integration.is_integrated">
            <template v-slot:icon>
                <div class="flex items-center justify-center h-9 w-9 rounded shadow bg-neutral-100 mt-0.5">
                    <Icon icon="mdi:transit-connection-variant" class="text-nearylight-100 w-5 h-5" />
                </div>
            </template>
            <div class="leading-7">
                <div class="text-field-default-foreground text-sm font-medium">{{ integration.display_name }}
                </div>
                <div class="text-sm text-nearygray-400"></div>
            </div>
            <template v-slot:button>
                <Button v-if="integration.is_integrated" @click="disconnectIntegration(integration)"
                    button-type="btn-outline-light"
                    :class="['bg-nearyblue-50 text-nearygray-200 w-full sm:w-24 shrink-0 px-3 py-2 text-sm rounded']">
                    Disconnect
                </Button>
                <Button v-else @click="connectIntegration(integration)" button-type="btn-light"
                    :class="['w-full sm:w-24 shrink-0 px-3 py-2 text-sm rounded']">
                    Connect
                </Button>
            </template>
        </Card>
        </template>
    </div>
    <Modal :isOpen="isOpen" @save="save" @close="close">
        <template v-slot:title>
            <h3 class="font-semibold text-lg text-field-default-foreground">{{ openIntegration.display_name }}</h3>
        </template>
        <div class="flex-grow w-full my-5">
            <div>
                <input v-model="apiKey" type="text" placeholder="Enter your API key"
                    class="focus:ring-0 focus:border-nearyblue-300 border border-transparent rounded-md bg-nearygray-100 text-sm w-full px-3 py-2" />
            </div>
        </div>
        <template v-slot:buttons>
            <Button @buttonClick="save" button-type="btn-light" class="w-full">Save</Button>
            <Button @buttonClick="close" button-type="btn-outline-light" class="w-full">Cancel</Button>
        </template>
    </Modal>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAppStore } from '@/store/index.js';
import Card from './common/Card.vue'
import Modal from './common/Modal.vue'
import Button from './common/Button.vue'
import api from '../services/apiService';
import { Icon } from '@iconify/vue';

const store = useAppStore();

const integrations = ref([])

const connectIntegration = async (integration) => {
    if (integration.auth_method == 'oauth') {
        let oauth = await api.getOAuthURL(integration.id);
        if (oauth.auth_url) {
            window.location.href = oauth.auth_url;
        }
    } else {
        openIntegration.value = integration;
        openModal();
    }
};

const disconnectIntegration = async (integration) => {
    integrations.value = await api.disconnectIntegration(integration);
};

const isOpen = ref(false);
const apiKey = ref(null);
const openIntegration = ref(null);

const openModal = () => {
    isOpen.value = true;
};

const save = async () => {

    isOpen.value = false;
    openIntegration.value.api_key = apiKey;
    let updatedIntegrations = await api.saveIntegration(openIntegration.value);
    if (updatedIntegrations) {
        integrations.value = updatedIntegrations;
    }
};

const close = () => {
    isOpen.value = false;
};


onMounted(async () => {
    integrations.value = await api.getIntegrations();
})

</script>