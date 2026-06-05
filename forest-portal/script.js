let text = document.getElementById('text');
let plant_left = document.getElementById('plant_left');
let plant_right = document.getElementById('plant_right');
let portal = document.getElementById('portal');
let bg = document.getElementById('bg');

window.addEventListener('scroll', () => {
    let value = window.scrollY;

    text.style.marginTop = value * 2.5 + 'px';
    
    plant_left.style.left = value * -1.5 + 'px';
    plant_right.style.left = value * 1.5 + 'px';
    
    portal.style.top = value * -0.5 + 'px';
    
    bg.style.top = value * 0.5 + 'px';
});
