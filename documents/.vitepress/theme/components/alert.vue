<template>
    <div class="alert md-tip">
    <p class='md-title' v-if="have_title">
        <svg v-if="show_svg" :viewBox="`${svg_viewBox} ${svg_width} ${svg_height}`" version="1.1" :width="svg_width" :height="svg_height" aria-hidden="true" class="svg-alert" xmlns="http://www.w3.org/2000/svg"><path :d="svg_content"/></svg>
    {{ title }}
    </p>
    <p class='text'><slot /></p>
    </div>
</template>

<script setup>
defineOptions({
    name: 'alert'
})
defineProps({
    show_svg: {
        type: Boolean,
        default: false
    },
    have_title: {
        type: Boolean,
        default: false
    },
    svg_viewBox: {
        type: String,
        default: '0 0'
    },
    svg_width: {
        type: String,
        default: '16'
    },
    svg_height: {
        type: String,
        default: '16'
    },
    svg_content: {
        type: String,
        default: 'Z'
    },
    title: {
        type: String,
        default: ''
    }
})
</script>

<style scoped>
.alert {
    margin: 10px 0;
    padding-left: 5px;
    word-wrap: break-word;
    line-height: 1.5;
    font-family: -apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans",Helvetica,Arial,sans-serif,"Apple Color Emoji","Segoe UI Emoji";
    font-size: 14px;
    initial-value: 0;
    box-sizing: border-box;
    padding: 0 0;
    color: #1f2328;
}

.dark .alert {
    color: #f0f6fc;
}
</style>
<style scoped src="./alert.css"></style>