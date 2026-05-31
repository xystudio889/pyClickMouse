<template>
    <input type="text" :value="text" class="ginput" :placeholder="place"></input>
</template>

<script setup>
defineOptions({
    name: 'ginput'
})
defineProps({
    text: {
        type: String,
        default: '',
    },
    place: {
        type: String,
        default: '',
    }
})
</script>

<style scoped>
.ginput {
    background-color: white;
    margin: 10px 0px;
    margin-top: 0;
    padding: 5px .75rem;
    border-radius: 5px;
    border: solid 1px #d8dde0;
    appearance: none;
    color: black;
    font-family: inherit;
    font-size: inherit;
    width: 100%;
    cursor: text;
    outline: none;
}

.ginput::placeholder {
    color: #9198a1;
}

.ginput:focus,
.dark .ginput:focus
{
    border: 2px solid #1f6feb;
}

.dark .ginput {
    background-color: #0d1117;
    color: white;
    border-color: #3d444d;
}
</style>