// // Wait for the DOM to fully load
// document.addEventListener('DOMContentLoaded', function () {
//     const serviceImages = {
//         plumber: [
//             'https://thumbs.dreamstime.com/b/indian-plumber-using-screwdriver-fixing-boiler-water-heater-working-heating-system-apartment-indian-plumber-using-335061953.jpg',
//             'https://cdn.pixabay.com/photo/2016/11/19/14/51/plumber-1840631_1280.jpg',
//             'https://st2.depositphotos.com/6235482/10317/i/450/depositphotos_103173498-stock-photo-handyman-with-tools.jpg',
//         ],
//         builder: [
//             'https://c8.alamy.com/comp/2RG8PGF/two-indian-male-and-female-civil-engineers-or-architect-wearing-helmet-and-vest-holding-paperwork-blueprint-at-construction-site-discussing-real-estat-2RG8PGF.jpg',
//             'https://st2.depositphotos.com/6235482/10317/i/450/depositphotos_103173498-stock-photo-handyman-with-tools.jpg',
//             'https://cdn.pixabay.com/photo/2016/05/05/03/09/civil-engineer-1385628_1280.jpg',
//         ],
//         cook: [
//             'https://t4.ftcdn.net/jpg/01/41/71/73/360_F_141717314_WSq1TJzC98sAHTrnYejY7niRfcR6cE6y.jpg',
//             'https://cdn.pixabay.com/photo/2017/09/25/01/15/cooking-2788940_1280.jpg',
//             'https://media.istockphoto.com/id/172169125/photo/chef-in-kitchen.jpg?s=612x612&w=0&k=20&c=7ilbDEoH6RycCBVBNpsPuvx8EunU2cXSRiV2fWlLqigA=',
//         ],
//         painter: [
//             'https://media.istockphoto.com/id/498456340/photo/painter-in-white-dungarees-blue-t-shirt.jpg?s=612x612&w=0&k=20&c=EWfLHtOEYiW-U0BZn6s-juR3oMuz4cT1WbLuQmGBU2k=',
//             'https://cdn.pixabay.com/photo/2016/11/21/17/17/painter-1853773_1280.jpg',
//             'https://www.shutterstock.com/image-photo/smiling-30s-latin-hispanic-middleaged-260nw-2491645993.jpg',
//         ],
//     };

//     const serviceSelect = document.getElementById('serviceSelect');
//     const imageContainer = document.getElementById('imageContainer');

//     // Function to update images based on selected service
//     function updateImages(service) {
//         imageContainer.innerHTML = ''; // Clear existing images
//         const images = serviceImages[service] || [];
//         images.forEach((url) => {
//             const img = document.createElement('img');
//             img.src = url;
//             img.alt = `${service} service image`;
//             img.style.width = '100%'; // Set the width of images
//             img.style.marginBottom = '10px'; // Add some spacing between images
//             imageContainer.appendChild(img);
//         });
//     }

//     // Event listener for service selection change
//     serviceSelect.addEventListener('change', function () {
//         updateImages(this.value);
//     });
// });
