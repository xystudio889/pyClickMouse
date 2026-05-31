<template>
    <alert :title="title || 'Note'" have_title="true" show_svg="true" svg_content="M0 -2H1A1 1 0 0 1 2 -1V5A1 1 0 0 1 1 6H1A1 1 0 0 1 0 5V-1A1 1 0 0 1 2 -1M7 -2H8A1 1 0 0 1 9 -1V5A1 1 0 0 1 8 6H8A1 1 0 0 1 7 5V-1A1 1 0 0 1 9 -1M-3 0H11A1 1 0 0 1 12 1V2H-3V1A1 1 0 0 1 -2 0M-3 1H-1V20H-2A1 1 0 0 1 -3 19M-1 18H12V19A1 1 0 0 1 11,20H-1V18M 10 18H12V2H10M1 6.5H8A1 1 0 0 1 9 7.5V7.75A1 1 0 0 1 8 8.75H1A1 1 0 0 1 0 7.75A1 1 0 0 1 0 6.75M1 10H8A1 1 0 0 1 9 11V11.25A1 1 0 0 1 8 12.25H1A1 1 0 0 1 0 11.25A1 1 0 0 1 0 10.25M1 13.5H8A1 1 0 0 1 9 14.5V14.75A1 1 0 0 1 8 15.75H1A1 1 0 0 1 0 14.75A1 1 0 0 1 0 13.75Z" >
    <slot />
    </alert>
</template>

<script setup>
import alert from './alert.vue';

defineOptions({
  name: 'Note'
})
defineProps({
    title: {
        type: String,
        default: '',
    },
})
</script>

<style scoped>
* {
    --color: #1f6feb;
}
</style>