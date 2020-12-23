const socket = new WebSocket(`ws://${document.location.hostname}:${WSPort}`)

class PTMLError extends Error {}

function evaluate(str)
{
        eval(str)
}

function ThrowError(err)
{
        throw new PTMLError(err)
}

function Create(element)
{
        document.body.innerHTML+=element
}

function ChangeInner(id, text)
{
        let element = document.getElementsByClassName(`ptml-id-${id}`)
        if(element.length>0) element[0].innerHTML = text
}

Functions = {
        "eval":evaluate,
        "throw":ThrowError,
        "create":Create,
        "ChangeInner":ChangeInner
}

socket.onopen = _ => socket.send(`SetRoute ${document.location.pathname}`)

socket.onmessage = event => {
        let message = event.data
        let splitted = message.split(" ")
        let instruction = splitted[0]
        let arguments = splitted.slice(1)
        if(instruction in Functions)
        {
                let parameters = arguments.slice(0, Functions[instruction].length-1)
                parameters.push(arguments.slice(Functions[instruction].length-1).join(" "))
                Functions[instruction](...parameters)
        }
        else console.log(`Got unknown instruction: ${instruction}`)
}

window.onload = _ => {
        for(let element of document.getElementsByTagName("*")){
                element.className.split(" ").forEach(name => {
                        let found = name.match(/^ptml-attribute-(.*?)-(.*?)$/g)
                        if(found)
                        {
                                found = found[0].split("-").slice(2)
                                let attrib = found[0]
                                let func = found.slice(1).join("-")
                                element[attrib] = () => socket.send(`call {func}`)
                        }
                })
        }
}