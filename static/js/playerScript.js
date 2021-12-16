const socket = io(); //conexion
// controles
const play = document.querySelector(".play");
const previous = document.querySelector(".prev");
const next = document.querySelector(".next");
// audio
const track = document.querySelector("audio");
// info
const title = document.querySelector(".title");
const artista = document.querySelector('.artista');
const album = document.querySelector('.album');
const reprNow = document.querySelector('.repr-now');
// volumen
const showVolume = document.querySelector("#show-volume");
const volumeIcon = document.querySelector("#volume-icon");
const currentVolume = document.querySelector("#volume");
// duracion
const tiempoActual = document.querySelector(".current-time");
const duracionCancion = document.querySelector(".duration-time");
const slider = document.querySelector(".duration-slider");

// playList
const musicPlaylist = document.querySelector(".music-playlist");
const pDiv = document.querySelector(".playlist-div");
const pDivv = document.querySelector(".tabla-body");
const playList = document.querySelector(".playlist");

const btnhideshow = document.querySelector('.btndesplegar');
const columna = document.querySelector('.columna')
const column2 = document.querySelector('.columna2')
//const toogle = document.querySelector('.tabladatos')

let timer;
let autoplay = 0;
let indexTrack = 0;
let songIsPlaying = false;

let btnhide = false;


function newfunc(){
  if (btnhide == false) {
    mostrar();
  }
  else if ((btnhide == true)) {
    ocultar(); 
  }
};

function mostrar(){
  columna.classList.remove('d-none','d-sm-block', 'd-md-none', 'd-lg-block', 'd-sm-none', 'd-md-block');
  column2.classList.add('d-none','d-sm-block','d-md-none', 'd-lg-block', 'd-sm-none', 'd-md-block');
  btnhide = true;
};

function ocultar(){
  columna.classList.add('d-none','d-sm-block', 'd-md-none', 'd-lg-block', 'd-sm-none', 'd-md-block');
  column2.classList.remove('d-none','d-sm-block','d-md-none', 'd-lg-block', 'd-sm-none', 'd-md-block');
  btnhide = false;
};





// eventos
btnhideshow.addEventListener("click", newfunc); // reproducir y pausar
play.addEventListener("click", justPlay); // reproducir y pausar
next.addEventListener("click", nextSong); // siguiente cancion
previous.addEventListener("click", prevSong); // anterior cancion
volumeIcon.addEventListener("click", muteSound); // mute
currentVolume.addEventListener("change", changeVolume); // cambiar volumen
slider.addEventListener("change", progressDuracion); // cambiar duracion
track.addEventListener("timeupdate", songTimeUpdate); // duracion automatica

// cargar pistas
function loadTrack(indexTrack) {
    clearInterval(timer);
    resetSlider();
  
    track.src = '/playMusic/' + listSongs[indexTrack].cancion;
    title.innerHTML = listSongs[indexTrack].titulo;
    artista.innerHTML = listSongs[indexTrack].artista;
    album.innerHTML = listSongs[indexTrack].album;
    
    track.load();
    

    timer = setInterval(updateSlider, 1000);
}

loadTrack(indexTrack);

// chequea si hay algo reproduciendose
function justPlay() {
    if (songIsPlaying == false) {
      playSong();
    } else {
      pauseSong();
    }
}

// reproduce la cancion
function playSong() {
    track.play();
    songIsPlaying = true;
    socket.send("play");
    play.innerHTML = '<i class="fal fa-pause-circle" id="iconapp"></i>';
    reprNow.innerHTML = 'Reproduciendo ahora';
    socket.emit('songsData', {"titulo_cancion" : listSongs[indexTrack].titulo,
    "nombre_artista" : listSongs[indexTrack].artista,
    "nombre_album" : listSongs[indexTrack].album,
    "estado" : songIsPlaying});
}

// pausa la cancion
function pauseSong() {
    track.pause();
    socket.send("pause");
    songIsPlaying = false;
    play.innerHTML = '<i class="fal fa-play-circle" id="iconapp"></i>';
    reprNow.innerHTML = 'En pausa';
    socket.emit('songsData', {"titulo_cancion" : listSongs[indexTrack].titulo,
    "nombre_artista" : listSongs[indexTrack].artista,
    "nombre_album" : listSongs[indexTrack].album,
    "estado" : songIsPlaying});
}

// siguiente cancion
function nextSong(){
    if (indexTrack < listSongs.length - 1) {
      indexTrack++;
      loadTrack(indexTrack);
      socket.send("next");
      playSong();
    } else {
      indexTrack = 0;
      loadTrack(indexTrack);
      socket.send("next");
      playSong();
    }
}
  
// anterior cancion
function prevSong() {
    if (indexTrack > 0) {
      indexTrack--;
      loadTrack(indexTrack);
      playSong();
    } else {
      indexTrack = listSongs.length - 1;
      loadTrack(indexTrack);
      playSong();
    }
}

// mutear volumen
function muteSound() {
    track.volume = 0;
    showVolume.innerHTML = 0;
    currentVolume.value = 0;
}

//recibir valor de volumen
function changeVolumes(valor) {
  showVolume.innerHTML = valor;    
  track.volume = valor / 100;
  currentVolume.value = valor;
}

// cambiar volumen
function changeVolume() {
    showVolume.innerHTML = currentVolume.value;    
    track.volume = currentVolume.value / 100;
    vol = currentVolume.value
    socket.emit("volumeC", vol)
}



// Change Duration
function progressDuracion() {
    let sliderPosition = track.duration * (slider.value / 100);
    track.currentTime = sliderPosition;
}

// Reste Slider
function resetSlider() {
    slider.value = 0;
}
  
  // Update Slider
function updateSlider() {
    let position = 0;
  
    if (!isNaN(track.duration)) {
      position = track.currentTime * (100 / track.duration);
      slider.value = position;
    }
  
    if (track.ended) {
      play.innerHTML = '<i class="fal fa-play-circle" id="iconapp">';
      if (autoplay == 0 && indexTrack < listSongs.length - 1) {
        indexTrack++;
        loadTrack(indexTrack);
        playSong();
      } else if (autoplay == 0 && indexTrack == listSongs.length - 1) {
        indexTrack = 0;
        loadTrack(indexTrack);
        playSong();
      }
    }
}

// Update Current song time
function songTimeUpdate() {
    if (track.duration) {
      let curmins = Math.floor(track.currentTime / 60);
      let cursecs = Math.floor(track.currentTime - curmins * 60);
      let durmins = Math.floor(track.duration / 60);
      let dursecs = Math.floor(track.duration - durmins * 60);
  
      if (dursecs < 10) {
        dursecs = "0" + dursecs;
      }
      if (durmins < 10) {
        durmins = "0" + durmins;
      }
      if (curmins < 10) {
        curmins = "0" + curmins;
      }
      if (cursecs < 10) {
        cursecs = "0" + cursecs;
      }
      tiempoActual.innerHTML = curmins + ":" + cursecs;
      duracionCancion.innerHTML = durmins + ":" + dursecs;
    } else {
      tiempoActual.innerHTML = "00" + ":" + "00";
      duracionCancion.innerHTML = "00" + ":" + "00";
    }
}

// Display Tracks in playlist
let counter = 1;
function displayTracks() {
  for (let i = 0; i < listSongs.length; i++) {
    console.log(listSongs[i].cancion);
    
    //let divv = document.createElement("tbody");
    let div = document.createElement("tr");
    //div.classList.add("playlist-s");
    div.classList.add("playlist-sr");
    div.innerHTML = `
        <th class="song-index">${counter++}</th>
        <td class="single-song text-light">${listSongs[i].titulo}</td>
    `;
    pDivv.appendChild(div);
  }
  playFromPlaylist();
}

displayTracks();

// Play song from the playlist
function playFromPlaylist() {
    pDivv.addEventListener("click", (e) => {
      if (e.target.classList.contains("single-song")) {
      
        const indexNum = listSongs.findIndex((item, index) => {
          if (item.titulo === e.target.innerHTML) {
            return true;
          }
        });
        //console.log(indexNum);
        loadTrack(indexNum);
        indexTrack = indexNum;
        console.log(indexTrack);
        playSong();
     
      }
    });
}
let albumName;

socket.on("message", (msg) => {
  console.log(msg);
  if (msg=='pausar') {
    pauseSong(); 
  } else if (msg=='reproducir') {
    playSong();
  } else if (msg=='siguiente') {
    nextSong();
  } else if (msg=='anterior') {
    prevSong();
  } else if (msg == 'estado Inicial') {
    
    socket.emit('songsData', {"titulo_cancion" : listSongs[indexTrack].titulo,
                              "nombre_artista" : listSongs[indexTrack].artista,
                              "nombre_album" : listSongs[indexTrack].album,
                              "estado" : songIsPlaying});
    
  }
});

socket.on("volumeC", (valor) => {
  changeVolumes(valor)
});

socket.send(songIsPlaying)

