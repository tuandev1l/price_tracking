const turnOnSlide = document.querySelector('#turn_on_slide');
const turnOnValue = document.querySelector('.humid_turn_on__value');
const turnOffSlide = document.querySelector('#turn_off_slide');
const turnOffValue = document.querySelector('.humid_turn_off__value');

// console.log(turnOffSlide, turnOnSlide);
turnOnSlide.oninput = function () {
  turnOnValue.innerText = this.value + '%';
};

turnOffSlide.oninput = function () {
  turnOffValue.innerText = this.value + '%';
};
