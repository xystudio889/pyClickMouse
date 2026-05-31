<template>
    <span class='title'>
        <span class='title-text' :class="{ 'nomargin': noTopMargin}"><slot /></span>
        <span class='must-select' v-if="required" :class="{ 'nomargin': noTopMargin}">*</span>
    </span>
    <p class="desc" v-if="desc !== ''">{{ desc }}</p>
</template>

<script setup>
defineOptions({
    name: 'subtitle'
})
defineProps({
    required: {
        type: Boolean,
        default: false,
    },
    desc: {
        type: String,
        default: '',
    },
    noTopMargin: {
        type: Boolean,
        default: false,
    }
})
</script>

<style scoped>
.title {
    display: flex;
    column-gap: .25rem;
    font-weight: 600;
}

.title-text {
    margin-right: .25rem;
    margin-top: 1rem;
    margin-bottom: .5rem;
    font-size: .875rem;
    color: inherit;
    cursor: pointer;
}

.title-text.nomargin {
    margin-top: 0;
}

.must-select {
    color: #f85149;
    margin-top: 1rem;
}

.must-select.nomargin {
    margin-top: 0;
}

.desc {
    color: #9198a1;
    font-size: 12px;
    margin: 0;
    margin-bottom: 0.75rem;
}
</style>