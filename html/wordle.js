var guess_size = 6;
var letter_size = 5;

var guess_count = 0;
var letter_count = 0;

var done = false;
var win = false;

var popup_on = true;
var bool_insane = false;

// Markings
const BLANK = 0;
const GOOD = 1;
const PERFECT = 2;

const keyboard = [
    ['Q', 'W', 'E', 'R', 'T', 'U', 'I', 'IE', 'O', 'P'],
    ['A', 'S', 'D', 'F', 'G', 'Ħ', 'H', 'GĦ', 'J', 'K', 'L'],
    ['⏎', 'Z', 'Ż', 'X', 'Ċ', 'V', 'Ġ', 'B', 'N', 'M', '⌫']
]

word_frequencies = {};

// List of words
game_words = [('unita').split(""), ('tajba').split("")];
player_words = [('unita').split(""), ('tajba').split(""), ('marka').split("")];

// Need to make the choosing function
var word_chosen = ("unita").split("");

var hist = []; // [ "unita", "(1, 1, 1, 1, 1)", "tajba", "(2, 2, 2, 2, 2)" ]

window.onload = function()
{
    load();
    start();
}

function start()
{
    // Wordle
    for (let i = 0; i < guess_size; i++)
    {
        for (let j = 0; j < letter_size; j++)
        {
            let tile = document.createElement("span");
            tile.id = i.toString() + "-" + j.toString();
            tile.classList.add("tile");
            tile.innerText = "";
            document.getElementById("game").appendChild(tile);
        }
    }

    // Keyboard
    for (let i = 0; i < keyboard.length; i++)
    {
        var current_row = keyboard[i];
        var keyboard_row = document.createElement("div");
        keyboard_row.classList.add("keyboard-row");

        for (let j = 0; j < current_row.length; j++)
        {
            var key_tile = document.createElement("div");
            var key = current_row[j];
            key_tile.innerHTML = key;

            // Check of big / small
            if (key == "⏎") key_tile.id = "Enter";
            else if (key == "⌫") key_tile.id = "Backspace";
            else key_tile.id = "Key" + key;

            key_tile.addEventListener("click", inputKey);
            key_tile.classList.add("key-tile");
            key_tile.classList.add("disable-select");
            keyboard_row.appendChild(key_tile);
        }
        document.body.appendChild(keyboard_row);
    }
}

function restart(same_word=false)
{
    // Game
    if (!same_word) ranadom_word_start();
    done = false;
    win = false;
    guess_count = 0;
    letter_count = 0;
    hist = [];

    // Wordle
    for (let i = 0; i < guess_size; i++)
    {
        for (let j = 0; j < letter_size; j++)
        {
            tile_id = i.toString() + "-" + j.toString();
            tile = document.getElementById(tile_id);
            tile.innerText = "";
            tile.classList.remove("good");
            tile.classList.remove("perfect");
            tile.classList.remove("blank");
        }
    }

    // Keyboard
    for (let i = 0; i < keyboard.length; i++)
    {
        var current_row = keyboard[i];
        for (let j = 0; j < current_row.length; j++)
        {
            key = current_row[j];

            if (key == "⏎") key_id = "Enter";
            else if (key == "⌫") key_id = "Backspace";
            else key_id = "Key" + key;

            // console.log(key_id);

            var key_tile = document.getElementById(key_id);
            key_tile.classList.remove("good");
            key_tile.classList.remove("perfect");
            key_tile.classList.remove("blank");
        }
    }

    // Answer
    document.getElementById("answer").innerHTML = "";
}

function getTile(place=letter_count)
{
    return document.getElementById(guess_count.toString() + "-" + place.toString());
}

function updateKeyTile(letter, mark)
{
    var key_tile_CL = document.getElementById("Key" + letter.toLocaleUpperCase()).classList;

    class_name = "";
    if (mark == PERFECT) 
    {
        key_tile_CL.remove("good");
        key_tile_CL.remove("blank");
        key_tile_CL.add("perfect");
    }
    else if (mark == GOOD && !key_tile_CL.contains("perfect"))
    {
        key_tile_CL.remove("blank");
        key_tile_CL.add("good");
    }
    else if (mark == BLANK && !key_tile_CL.contains("perfect") && !key_tile_CL.contains("good")) 
    {
        key_tile_CL.add("blank");
    }
}

document.addEventListener("keyup", (e) => 
{
    if (bool_insane) return;

    inputHandler(e);
})

function inputKey()
{
    if (bool_insane) return;

    var e = {"code": this.id};
    // console.log(e);
    inputHandler(e);
}

function inputHandler(e)
{
    if (done) return;

    var eCode = e.code;
    if ("KeyA" <= eCode && eCode <= "KeyŻ")
    {
        if (letter_count < letter_size)
        {
            var currentTile = getTile();
            if (currentTile.innerText == "") 
            {
                currentTile.innerText = eCode.slice(3);
                letter_count += 1;
            }
        }
    }
    else if (eCode == "Backspace")
    {
        if (letter_count > 0 && letter_count <= letter_size)
        {
            letter_count -= 1;
            getTile().innerText = "";
        }
        
    }
    else if (eCode == "Enter" && letter_count == letter_size)
    {
        // Getting word
        var word_guess = new Array(letter_size);
        for (let i = 0; i < letter_size; i++)
        {
            word_guess[i] = getTile(i).innerHTML.toLocaleLowerCase();
        }
        if (checkValid(word_guess) == true)
        {
            checkGuess(word_guess);
            guess_count += 1;
            letter_count = 0;
        }
    }

    // If failed :(
    if (!done && guess_count == guess_size)
    {
        done = true;
        document.getElementById("answer").innerHTML = word_chosen.join("");
    }
}

function checkValid(word_guess)
{
    var valid = false;

    if (player_words.some(something => something.join("") === word_guess.join(""))) valid = true;

    if (!valid)
    {
        var popup = document.getElementById("popup");
        popup.innerHTML = "The word \'" + word_guess.join("") + "\' is not in the dictionary";
        popup.classList.add("show");
        

        // To bypass the spam of the show button :/
        if (!popup_on) popup_on = true;
        else{
            
            // https://bobbyhadz.com/blog/javascript-hide-element-after-few-seconds
            setTimeout(() => {
                popup.classList.remove("show");
                popup_on = false;
            }, 3000);
        }
    }

    return valid;
}

function checkGuess(word_guess)
{
    var marking = new Array(letter_size).fill(0);
    
    // Go through letter frequencies, and perfect letters
    var freq_letters_in_chosen = {};
    for (let i = 0; i < letter_size; i++)
    {
        var letter = word_chosen[i];
        
        // Mark perfect letters
        if (letter == word_guess[i])
        {
            marking[i] = PERFECT;
            getTile(i).classList.add("perfect");
            updateKeyTile(letter, PERFECT);
        }
        else // Update frequencies
        {
            freq_letters_in_chosen[letter] = freq_letters_in_chosen[letter] ? freq_letters_in_chosen[letter] + 1 : 1;
        }
    }

    // Check if finished
    if (marking.every(e => e == PERFECT))
    {
        done = true;
        win = true;
        return;
    }

    // console.log(freq_letters_in_chosen);

    // Checking for GOOD
    for (let i = 0; i < letter_size; i++)
    {
        var letter = word_guess[i];
        if (word_chosen.includes(letter))
        {
            if (marking[i] == BLANK)
            {
                if (freq_letters_in_chosen[letter] > 0)
                {
                    marking[i] = GOOD;
                    freq_letters_in_chosen[letter] -= 1;
                }
            }
        }
    }

    // console.log(freq_letters_in_chosen);

    // Updating html with GOOD and BLANK
    for (let i = 0; i < letter_count; i++)
    {
        if (marking[i] == GOOD)
        {
            getTile(i).classList.add("good");
            updateKeyTile(word_guess[i], GOOD);
        }
        else if (marking[i] == BLANK)
        {
            getTile(i).classList.add("blank");
            updateKeyTile(word_guess[i], BLANK);
        }
    }

    hist.push(ex_toString(word_guess));
    hist.push('(' + marking.toString().replaceAll(',', ', ') +')');
}

function ranadom_word_start()
{
    const random = Math.floor(Math.random() * game_words.length);
    word_chosen = game_words[random];
    // word_chosen = expand_word("ponta");
}

function solution()
{
    // if (done) return;
    // word_next = expand_word("unita");

    // for (let i = 0; i < letter_size; i++)
    // {
    //     getTile(i).innerHTML = word_next[i];
    //     letter_count = letter_size;
    // }

    // var e = {"code": "Enter"};
    // inputHandler(e);
    document.getElementById("solver").classList.toggle("show");
}

// https://www.sitepoint.com/delay-sleep-pause-wait/
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }


async function solve_once(trees)
{
    if (bool_insane) return;
    bool_insane = true;
    restart(true);

    // var insane_button = document.getElementById("insane");
    // insane_button.classList.add("active");

    for (let j = 0; j < guess_size; j++) {

        word_next = get_word_wt(hist, trees);

        for (let i = 0; i < letter_size; i++)
        {
            getTile(i).innerHTML = word_next[i];
            await sleep(1);
        }
        letter_count = letter_size;
        var e = {"code": "Enter"};
        inputHandler(e);

        if (win) 
        {
            break;
        }
    }
    // insane_button.classList.remove("active");
    // document.getElementById("answer").innerHTML = "Rounds: " + rounds +",\tWins: " + wins + ",\tAverage guess: " + (sum_guess/rounds);
    bool_insane = false;
}

async function insane()
{
    if (bool_insane) return;
    bool_insane = true;
    restart();

    var insane_button = document.getElementById("insane");
    insane_button.classList.add("active");

    var rounds = 100;
    var wins = 0;
    var sum_guess = 0;

    for (let k = 0; k < rounds; k++)
    {
        // Updaing stats
        insane_button.classList.remove("active");
        document.getElementById("answer").innerHTML = "Rounds: " + k +",\tWins: " + wins + ",\tAverage guess: " + (sum_guess/k);
        
        for (let j = 0; j < guess_size; j++) {
            sum_guess += 1;

            word_next = get_word_wt(hist, frequency_explore);

            for (let i = 0; i < letter_size; i++)
            {
                getTile(i).innerHTML = word_next[i];
                await sleep(1);
            }
            letter_count = letter_size;
            var e = {"code": "Enter"};
            inputHandler(e);

            if (win) 
            {
                wins += 1;
                break;
            }
        }

        restart();
    }
    
    // Updaing stats
    insane_button.classList.remove("active");
    document.getElementById("answer").innerHTML = "Rounds: " + rounds +",\tWins: " + wins + ",\tAverage guess: " + (sum_guess/rounds);
    bool_insane = false;
}


// Function to 'load JSON' data
function load() 
{
    words = []
    word_frequencies = {}
    temp_words = frequency;
    for (var word in temp_words)
    {
        var count = temp_words[word];
        if (count > 1) 
        {
            words.push(expand_word(word));
            word_frequencies[word] = count;
        }
    }

    // console.log(words);

    player_words = words;
    game_words = words;
    // player_words = JSON.parse(wordsDICTIONARY);
    // game_words = JSON.parse(words);
    // word_trees = word_trees;
    // word_trees_freq = word_trees_freq;

    ranadom_word_start();
}

function dark_mode()
{
    darkMode = "dark-mode";
    document.body.classList.toggle(darkMode);
    
    // document.getElementById("game").classList.toggle(darkMode);

    if (document.body.classList.contains(darkMode))
    {
        document.getElementById("dark-mode").innerHTML = "☽";
    }
    else
    {
        document.getElementById("dark-mode").innerHTML = "☀";
    }
}

// SHOWING STATS (HELPER)
function showstats()
{
    // this_frequency = word_frequencies;  // Update

    // bar_frequency = []
    // for (var word in this_frequency)
    // {
    //     temp_dict = {};
    //     temp_dict['x'] = word;
    //     temp_dict['value'] = this_frequency[word];
    //     bar_frequency.push(temp_dict);
    // }
    


    // document.getElementById("stats").classList.toggle("show");

    // if (document.getElementById("stats").classList.contains("show")) 
    // {
    //     var chart = anychart.bar();
    //     chart.title('Website Traffic Stats');
    //     chart.xAxis().title("Website");
    //     chart.yAxis().title("Traffic Per Minute");
    //     var series = chart.bar(bar_frequency);
    //     chart.container("stats");
    //     chart.restart();
    //     chart.draw();
    // }
}