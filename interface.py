# import pygame, sys
# from pygame.locals import *
# import numpy as np
# import time





import pygame
import time 
StimTimer = False
filename = 'default.csv'

y1 = 0
y2 = 0
y3 = 0
y4 = 0
y5 = 0
     
n1 = 0
n2 = 0
n3 = 0
n4 = 0
n5 = 0

TMS_Mark = False

def main():
    global StimTimer
    global y1
    global y2
    global y3
    global y4
    global y5
    
    global n1
    global n2
    global n3
    global n4
    global n5
    
    global TMS_Mark
    
    global filename 
    
    

    
    
    
    pygame.init()
    pygame.display.init()      
    disp = pygame.display.Info()
    WINDOWWIDTH = disp.current_w    
    WINDOWHEIGHT = disp.current_h
    size = [WINDOWWIDTH,WINDOWHEIGHT]

    
    
    


    
    # # Set up the colours (RGB values)
    BLACK     = (0  ,0  ,0  )
    GREY      = (120  ,120  ,120  )
    WHITE     = (255,255,255)
    YELLOW    = (255,255,0)
    ORANGE    = (255,165,0)
    RED       = (255,0,0)
    CYAN      = ( 52, 221, 221)

    BASICFONT = pygame.font.Font('freesansbold.ttf', 40)

    # #Window parameters

    LINETHICKNESS = 10





    screen = pygame.display.set_mode(size)
    pygame.mouse.set_visible(1)
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill(GREY)
    screen.blit(background, (0,0))
    pygame.display.flip()

    ## set-up screen in these lines above ##

    button = pygame.image.load('thing.png').convert_alpha()
    YES = pygame.image.load('YES.png').convert_alpha()
    NO = pygame.image.load('NO.png').convert_alpha()
    B1 = pygame.image.load('1.png').convert_alpha()
    B2 = pygame.image.load('2.png').convert_alpha()
    B3 = pygame.image.load('3.png').convert_alpha()
    B4 = pygame.image.load('4.png').convert_alpha()
    B5 = pygame.image.load('5.png').convert_alpha()
    CONFIRM = pygame.image.load('CONFIRM.png').convert_alpha()

    pygame.display.flip()

    QuitFlag = False
    Confidence = 0
    Phosphene = 0
    Reticle = False
    RedReticle = False
    Responses = []
    #StimTimer = False
    StimGuard = time.time() - 10 #This variable prevents stims more frequent than 1 per ten seconds
    SubjectResponseTime = 0
    Stage = 1
    Stim_TimeBenchmark = time.time()
    if filename[-4:] == '.csv':
        marks = open(filename + '_RESPONSES.csv', 'w')
    else:
        marks = open(filename[:-4] +  '_RESPONSES.csv', 'w')
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                ## if mouse is pressed get position of cursor ##
                pos = pygame.mouse.get_pos()
                ## check if cursor is on button ##
                if Confidence != 0:
                    if ConfirmButton.collidepoint(pos):
                        print('Take it to the bank boys!')
                        Responses.append(Phosphene)
                        Responses.append(Confidence)
                        if Phosphene == 1:
                            if Confidence == 1:
                                y1 = y1 +1
                            if Confidence == 2:          
                                y2 = y2 +1
                            if Confidence == 3:           
                                y3 = y3 +1
                            if Confidence == 4:           
                                y4 = y4 +1
                            if Confidence == 5:         
                                y5 = y5 +1
                        else:   #meaning if NoPhos   
                            if Confidence == 1:         
                                n1 = n1 +1
                            if Confidence == 2:         
                                n2 = n2 +1
                            if Confidence == 3:         
                                n3 = n3 +1
                            if Confidence == 4:         
                                n4 = n4 +1
                            if Confidence == 5:         
                                n5 = n5 +1
                        marks.write(str(Phosphene) + ',' + str(Confidence) + ',' + str(CountDownToStim-Stim_TimeBenchmark) + '\n')
                        Confidence = 0
                        Phosphene = 0
                        Stage = 1
                        SubjectResponseTime = time.time() - SubjectResponseTimer
                if Phosphene != 0:
                    if a.collidepoint(pos):
                        Confidence = 1 
                    if b.collidepoint(pos):
                        Confidence = 2
                    if c.collidepoint(pos):
                        Confidence = 3
                    if d.collidepoint(pos):
                        Confidence = 4            
                    if e.collidepoint(pos):
                        Confidence = 5
                if Stage == 4:
                    if A.collidepoint(pos):
                        Phosphene = -1
                    if B.collidepoint(pos):
                        Phosphene = 1                
            if event.type == pygame.KEYDOWN:  #press space to terminate pauses between blocs
                if event.key == pygame.K_q:
                    QuitFlag = True

        if StimTimer == True:
            if Stage == 1:
                Stage = 2
                if SubjectResponseTime > 3:
                    SubjectResponseTime = 3
                CountDownToStim = time.time() + 8 - SubjectResponseTime
                Reticle = True
                print CountDownToStim
            elif Stage == 2:
                if CountDownToStim < time.time() + 1:
                    Reticle = False
                    RedReticle = True
                if CountDownToStim < time.time():
                    TMS_Mark = True
                    print('stim happens now')
                    Stage = 3
            elif Stage == 3:
                if CountDownToStim < time.time() - 1:   
                    RedReticle = False
                    SubjectResponseTimer = time.time()
                    pygame.mouse.set_pos(WINDOWWIDTH/2, WINDOWHEIGHT/2)
                    Stage = 4
                    
        

        pygame.mouse.set_visible(0)
        if Stage == 4:
            pygame.mouse.set_visible(1)
            resultSurf = BASICFONT.render('    DID YOU SEE A PHOSPHENE?', True, WHITE)
            resultRect = resultSurf.get_rect()
            resultRect.center = (WINDOWWIDTH/2, 380)
            screen.blit(resultSurf, resultRect)
            A = screen.blit(NO, (WINDOWWIDTH/2 - 150, 420))
            B = screen.blit(YES, (WINDOWWIDTH/2 + 150, 420))

        if Reticle == True or StimTimer == False:
            pygame.draw.line(screen, WHITE, ((10+WINDOWWIDTH/2),WINDOWHEIGHT/2),((WINDOWWIDTH/2 - 10),WINDOWHEIGHT/2), (LINETHICKNESS/2))        
            pygame.draw.line(screen, WHITE, ((WINDOWWIDTH/2), 10+WINDOWHEIGHT/2),((WINDOWWIDTH/2),WINDOWHEIGHT/2-10), (LINETHICKNESS/2))
            
        if RedReticle == True:
            pygame.draw.line(screen, RED, ((10+WINDOWWIDTH/2),WINDOWHEIGHT/2),((WINDOWWIDTH/2 - 10),WINDOWHEIGHT/2), (LINETHICKNESS/2))        
            pygame.draw.line(screen, RED, ((WINDOWWIDTH/2), 10+WINDOWHEIGHT/2),((WINDOWWIDTH/2),WINDOWHEIGHT/2-10), (LINETHICKNESS/2)) 
            
        if Phosphene != 0:
            pygame.draw.rect(screen, CYAN, ((WINDOWWIDTH/2  + Phosphene*150 - 10  , 410),(120,87)), LINETHICKNESS)
            a = screen.blit(B1, (WINDOWWIDTH/2 -300, 670))
            b = screen.blit(B2, (WINDOWWIDTH/2 -150, 670))
            c = screen.blit(B3, (WINDOWWIDTH/2, 670))
            d = screen.blit(B4, (WINDOWWIDTH/2 + 150, 670))
            e = screen.blit(B5, (WINDOWWIDTH/2 + 300, 670))
            
            resultSurf = BASICFONT.render('     HOW CONFIDENT ARE YOU?', True, WHITE)
            resultRect = resultSurf.get_rect()
            resultRect.center = (WINDOWWIDTH/2, 630)
            screen.blit(resultSurf, resultRect)            
        
        if Confidence > 0:
            pygame.draw.rect(screen, CYAN, ((WINDOWWIDTH/2 -310 + ((Confidence-1)*150)  , 660),(120,87)), LINETHICKNESS)
            ConfirmButton = screen.blit(CONFIRM, (WINDOWWIDTH/2 - 100, 920))
        
        
        pygame.display.flip()
        pygame.display.update() 
        screen.fill(GREY)
        if QuitFlag == True:
            print(Responses)
            # markcounter = 0
            # for mark in Responses:
                # markcounter = markcounter + 1
                # marks.write(mark)
                # if markcounter == 1:
                    # marks.write(',')
                # else:
                    # marks.write('\n')
                    # markcounter = 0
            marks.close()
            
            
            pygame.quit()
            break
        
if __name__=='__main__':
    main()