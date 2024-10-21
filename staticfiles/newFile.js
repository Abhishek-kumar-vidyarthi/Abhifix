<script>
    const stickers = document.querySelectorAll('.sticker');
    let currentIndex = 0;

    function showSticker(index) {stickers.forEach((sticker, i) => {
        sticker.style.opacity = (i === index) ? 1 : 0;
    })}

    function changeSticker() {currentIndex = (currentIndex + 1) % stickers.length}// Loop through stickers
    ; // Loop through stickers
    showSticker(currentIndex);
    &rbrace;

    // Show the first sticker
    showSticker(currentIndex);
    setInterval(changeSticker, 5000); // Change every 5 seconds
</script>;
