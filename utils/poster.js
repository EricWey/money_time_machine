const POSTER_WIDTH = 960
const POSTER_HEIGHT = 1706

function roundRect(ctx, x, y, width, height, radius) {
  const safeRadius = Math.min(radius, width / 2, height / 2)
  ctx.beginPath()
  ctx.moveTo(x + safeRadius, y)
  ctx.lineTo(x + width - safeRadius, y)
  ctx.quadraticCurveTo(x + width, y, x + width, y + safeRadius)
  ctx.lineTo(x + width, y + height - safeRadius)
  ctx.quadraticCurveTo(x + width, y + height, x + width - safeRadius, y + height)
  ctx.lineTo(x + safeRadius, y + height)
  ctx.quadraticCurveTo(x, y + height, x, y + height - safeRadius)
  ctx.lineTo(x, y + safeRadius)
  ctx.quadraticCurveTo(x, y, x + safeRadius, y)
  ctx.closePath()
}

function fillRoundRect(ctx, x, y, width, height, radius, color) {
  ctx.save()
  roundRect(ctx, x, y, width, height, radius)
  ctx.setFillStyle(color)
  ctx.fill()
  ctx.restore()
}

function strokeRoundRect(ctx, x, y, width, height, radius, color, lineWidth) {
  ctx.save()
  roundRect(ctx, x, y, width, height, radius)
  ctx.setStrokeStyle(color)
  ctx.setLineWidth(lineWidth)
  ctx.stroke()
  ctx.restore()
}

function drawCenteredText(ctx, text, x, y, fontSize, color, weight) {
  ctx.save()
  ctx.setFillStyle(color)
  ctx.setTextAlign('center')
  ctx.setTextBaseline('middle')
  ctx.font = `${weight || 'normal'} ${fontSize}px serif`
  ctx.fillText(text, x, y)
  ctx.restore()
}

function wrapText(ctx, text, maxWidth) {
  const normalized = String(text || '').replace(/\r\n/g, '\n').split('\n')
  const lines = []

  normalized.forEach((paragraph) => {
    if (!paragraph) {
      lines.push('')
      return
    }

    let currentLine = ''
    paragraph.split('').forEach((char) => {
      const nextLine = currentLine + char
      if (ctx.measureText(nextLine).width > maxWidth && currentLine) {
        lines.push(currentLine)
        currentLine = char
      } else {
        currentLine = nextLine
      }
    })

    if (currentLine) {
      lines.push(currentLine)
    }
  })

  return lines
}

function drawMultilineText(ctx, text, x, y, maxWidth, lineHeight, fontSize, color) {
  ctx.save()
  ctx.setFillStyle(color)
  ctx.setTextAlign('left')
  ctx.setTextBaseline('top')
  ctx.font = `${fontSize}px serif`
  const lines = wrapText(ctx, text, maxWidth)
  lines.forEach((line, index) => {
    ctx.fillText(line || ' ', x, y + index * lineHeight)
  })
  ctx.restore()
  return lines.length
}

function drawBurst(ctx, centerX, centerY, radius, color) {
  ctx.save()
  ctx.translate(centerX, centerY)
  ctx.setStrokeStyle(color)
  ctx.setGlobalAlpha(0.16)
  for (let index = 0; index < 28; index += 1) {
    ctx.rotate((Math.PI * 2) / 28)
    ctx.beginPath()
    ctx.moveTo(0, -radius * 0.26)
    ctx.lineTo(0, -radius)
    ctx.stroke()
  }
  ctx.restore()
  ctx.setGlobalAlpha(1)
}

function drawPosterBorder(ctx) {
  strokeRoundRect(ctx, 34, 34, POSTER_WIDTH - 68, POSTER_HEIGHT - 68, 26, '#a61d18', 8)
  strokeRoundRect(ctx, 64, 64, POSTER_WIDTH - 128, POSTER_HEIGHT - 128, 20, '#cf8b32', 3)

  const corners = [
    [86, 86],
    [POSTER_WIDTH - 86, 86],
    [86, POSTER_HEIGHT - 86],
    [POSTER_WIDTH - 86, POSTER_HEIGHT - 86]
  ]

  corners.forEach(([x, y]) => {
    ctx.save()
    ctx.translate(x, y)
    ctx.setStrokeStyle('#a61d18')
    ctx.setLineWidth(4)
    for (let index = 0; index < 4; index += 1) {
      ctx.rotate(Math.PI / 2)
      ctx.beginPath()
      ctx.moveTo(0, -28)
      ctx.quadraticCurveTo(18, -16, 28, 0)
      ctx.stroke()
    }
    ctx.restore()
  })
}

function drawStamp(ctx, centerX, centerY, label) {
  ctx.save()
  ctx.translate(centerX, centerY)
  ctx.rotate(-0.16)
  ctx.setShadow(0, 14, 18, 'rgba(113, 21, 19, 0.22)')
  ctx.beginPath()
  ctx.arc(0, 0, 116, 0, Math.PI * 2)
  ctx.setFillStyle('#c93328')
  ctx.fill()
  ctx.setShadow(0, 0, 0, 'transparent')

  ctx.beginPath()
  ctx.arc(0, 0, 94, 0, Math.PI * 2)
  ctx.setLineWidth(4)
  ctx.setStrokeStyle('rgba(255, 230, 215, 0.72)')
  ctx.stroke()

  ctx.setTextAlign('center')
  ctx.setFillStyle('#ffe3d1')
  ctx.setTextBaseline('middle')
  ctx.font = 'bold 24px sans-serif'
  ctx.fillText('财富漂流认证章', 0, -50)
  ctx.font = 'bold 42px sans-serif'
  ctx.fillText(label, 0, 8)
  ctx.font = '22px sans-serif'
  ctx.fillText('OFFICIAL APPROVED', 0, 58)
  ctx.restore()
}

function drawPseudoCode(ctx, x, y, size, seedText) {
  fillRoundRect(ctx, x, y, size, size, 24, '#fffdf8')
  strokeRoundRect(ctx, x, y, size, size, 24, '#b18d58', 4)

  const padding = 24
  const moduleSize = (size - padding * 2) / 21
  const seed = String(seedText || '')

  function drawFinder(px, py) {
    fillRoundRect(ctx, px, py, moduleSize * 5, moduleSize * 5, 8, '#1d120c')
    fillRoundRect(ctx, px + moduleSize, py + moduleSize, moduleSize * 3, moduleSize * 3, 6, '#fffdf8')
    fillRoundRect(ctx, px + moduleSize * 2, py + moduleSize * 2, moduleSize, moduleSize, 4, '#1d120c')
  }

  drawFinder(x + padding, y + padding)
  drawFinder(x + size - padding - moduleSize * 5, y + padding)
  drawFinder(x + padding, y + size - padding - moduleSize * 5)

  for (let row = 0; row < 21; row += 1) {
    for (let col = 0; col < 21; col += 1) {
      const inFinder = (row < 5 && col < 5) || (row < 5 && col > 15) || (row > 15 && col < 5)
      if (inFinder) {
        continue
      }

      const source = seed.charCodeAt((row * 21 + col) % (seed.length || 1)) || 77
      if ((source + row * 7 + col * 13) % 3 === 0) {
        fillRoundRect(
          ctx,
          x + padding + col * moduleSize,
          y + padding + row * moduleSize,
          moduleSize - 1,
          moduleSize - 1,
          2,
          '#1d120c'
        )
      }
    }
  }
}

function drawPoster(ctx, payload) {
  ctx.setFillStyle('#efe0a8')
  ctx.fillRect(0, 0, POSTER_WIDTH, POSTER_HEIGHT)

  const bgGradient = ctx.createLinearGradient(0, 0, 0, POSTER_HEIGHT)
  bgGradient.addColorStop(0, '#f7e7b4')
  bgGradient.addColorStop(0.56, '#f4d892')
  bgGradient.addColorStop(1, '#ecd08c')
  ctx.setFillStyle(bgGradient)
  ctx.fillRect(0, 0, POSTER_WIDTH, POSTER_HEIGHT)

  drawBurst(ctx, POSTER_WIDTH / 2, 420, 350, '#b72820')
  drawPosterBorder(ctx)

  drawCenteredText(ctx, '财富漂流人生喜报', POSTER_WIDTH / 2, 130, 56, '#9f1814', 'bold')
  drawCenteredText(ctx, '谨以此报 表彰该同志的异地购买力表现', POSTER_WIDTH / 2, 190, 28, '#8a5d2f', 'bold')

  fillRoundRect(ctx, 124, 246, POSTER_WIDTH - 248, 112, 22, 'rgba(255, 249, 231, 0.72)')
  strokeRoundRect(ctx, 124, 246, POSTER_WIDTH - 248, 112, 22, '#c4964d', 3)
  drawCenteredText(ctx, `${payload.route} 财富调令`, POSTER_WIDTH / 2, 302, 34, '#5a2f1e', 'bold')

  fillRoundRect(ctx, 104, 392, POSTER_WIDTH - 208, 360, 30, 'rgba(255, 251, 240, 0.72)')
  strokeRoundRect(ctx, 104, 392, POSTER_WIDTH - 208, 360, 30, '#a61d18', 4)
  drawCenteredText(ctx, '等效月薪', POSTER_WIDTH / 2, 460, 34, '#8a5d2f', 'bold')
  drawCenteredText(ctx, `¥${payload.equivalentAmount}`, POSTER_WIDTH / 2, 566, 92, '#b11912', 'bold')
  drawCenteredText(ctx, `已达到当地中位收入的 ${payload.wealthRatio} 倍`, POSTER_WIDTH / 2, 654, 32, '#5a2f1e', 'bold')
  drawCenteredText(ctx, payload.moodTag, POSTER_WIDTH / 2, 710, 30, '#8c1f17', 'bold')

  drawStamp(ctx, 740, 840, payload.identityLabel)

  fillRoundRect(ctx, 90, 810, 470, 262, 26, 'rgba(255, 250, 239, 0.84)')
  strokeRoundRect(ctx, 90, 810, 470, 262, 26, '#c4964d', 3)
  drawCenteredText(ctx, '组织评语', 325, 858, 34, '#9f1814', 'bold')
  drawMultilineText(ctx, payload.summary, 128, 906, 394, 42, 28, '#513021')
  drawCenteredText(ctx, '特此通报，以资转发。', 325, 1030, 24, '#8a5d2f', 'bold')

  fillRoundRect(ctx, 90, 1108, POSTER_WIDTH - 180, 330, 28, 'rgba(255, 251, 240, 0.78)')
  strokeRoundRect(ctx, 90, 1108, POSTER_WIDTH - 180, 330, 28, '#a61d18', 3)
  drawCenteredText(ctx, 'AI 扎心文案', POSTER_WIDTH / 2, 1160, 36, '#9f1814', 'bold')
  const commentLines = drawMultilineText(ctx, payload.expertComment, 128, 1218, POSTER_WIDTH - 256, 44, 29, '#482c1b')
  drawCenteredText(ctx, `批注共 ${commentLines} 行，句句都往预算表上扎。`, POSTER_WIDTH / 2, 1390, 24, '#8a5d2f', 'bold')

  fillRoundRect(ctx, 90, 1472, POSTER_WIDTH - 180, 162, 24, 'rgba(164, 29, 24, 0.08)')
  strokeRoundRect(ctx, 90, 1472, POSTER_WIDTH - 180, 162, 24, '#c4964d', 3)
  drawPseudoCode(ctx, 126, 1496, 114, payload.route + payload.identityLabel + payload.equivalentAmount)
  drawMultilineText(
    ctx,
    '扫一扫进入小程序\n继续测算你的财富人生漂流轨迹',
    274,
    1518,
    420,
    38,
    28,
    '#5a2f1e'
  )
  drawCenteredText(ctx, '钱值时光机·财富漂流存档', 724, 1576, 28, '#9f1814', 'bold')

  drawCenteredText(ctx, '本海报由财富漂流宣传组 制作留念', POSTER_WIDTH / 2, 1662, 24, '#8a5d2f', 'bold')
}

function createPoster(canvasId, payload, component) {
  return new Promise((resolve, reject) => {
    const ctx = wx.createCanvasContext(canvasId, component)

    try {
      drawPoster(ctx, payload)
      ctx.draw(false, () => {
        wx.canvasToTempFilePath(
          {
            canvasId,
            width: POSTER_WIDTH,
            height: POSTER_HEIGHT,
            destWidth: POSTER_WIDTH,
            destHeight: POSTER_HEIGHT,
            fileType: 'png',
            quality: 1,
            success: (result) => resolve(result.tempFilePath),
            fail: () => reject(new Error('海报导出失败，请稍后重试。'))
          },
          component
        )
      })
    } catch (error) {
      reject(error)
    }
  })
}

module.exports = {
  POSTER_WIDTH,
  POSTER_HEIGHT,
  createPoster
}
