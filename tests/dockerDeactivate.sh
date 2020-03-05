#!/bin/bash
GW="$(route -n | awk '$1=="0.0.0.0" {print $2; exit}')"
echo "$GW" >~/my_gw
route del default gw "$GW"
